#!/usr/bin/env python3
"""
PrepKit template validator.

Checks each template against the JSON Schema, then applies the cross-field rules
the schema cannot express: extends resolution, merge-key integrity, substitute
and redundancy_group referential integrity, and pack-weight against any declared
target_weight_kg ceiling.

Usage:  python3 validate.py [template_dir]
Exit code is nonzero if any template fails, so this is CI-safe.
"""

import json
import pathlib
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).parent
SCHEMA = json.loads((ROOT / "schema" / "kit-template.schema.json").read_text())
MAX_DEPTH = 3

errors: list[str] = []
warnings: list[str] = []


def load_templates(dirpath: pathlib.Path) -> dict[str, dict]:
    out = {}
    for f in sorted(dirpath.glob("*.yaml")):
        doc = yaml.safe_load(f.read_text())
        tid = doc.get("id")
        if not tid:
            errors.append(f"{f.name}: missing required 'id'")
            continue
        if tid in out:
            errors.append(f"{f.name}: duplicate template id '{tid}'")
            continue
        doc["__file"] = f.name
        out[tid] = doc
    return out


def check_schema(templates: dict[str, dict]) -> None:
    validator = Draft202012Validator(SCHEMA)
    for tid, doc in templates.items():
        payload = {k: v for k, v in doc.items() if not k.startswith("__")}
        for err in sorted(validator.iter_errors(payload), key=lambda e: list(e.path)):
            path = "/".join(str(p) for p in err.path) or "(root)"
            msg = err.message
            # root-level conditional failures dump the whole document; unreadable
            if len(msg) > 200:
                msg = msg[:120].rsplit(" ", 1)[0] + " ... (see schema constraint)"
            errors.append(f"{doc['__file']}: {path}: {msg}")


def resolve(tid: str, templates: dict[str, dict], depth: int = 0) -> list[dict]:
    """Resolve a template's item list through its extends chain."""
    doc = templates[tid]
    parent_id = doc.get("extends")
    if not parent_id:
        return [dict(i) for i in doc.get("items", [])]
    if depth >= MAX_DEPTH:
        errors.append(f"{doc['__file']}: extends chain exceeds max depth {MAX_DEPTH}")
        return [dict(i) for i in doc.get("items", [])]
    if parent_id not in templates:
        errors.append(f"{doc['__file']}: extends unknown template '{parent_id}'")
        return [dict(i) for i in doc.get("items", [])]

    merged = {i["id"]: dict(i) for i in resolve(parent_id, templates, depth + 1)}
    for item in doc.get("items", []):
        iid = item["id"]
        if item.get("quantity") == 0:
            if iid not in merged:
                warnings.append(
                    f"{doc['__file']}: item '{iid}' has quantity 0 (removal) "
                    f"but is not present in parent '{parent_id}'"
                )
            merged.pop(iid, None)
        else:
            merged[iid] = dict(item)
    return list(merged.values())


def check_cross_field(tid: str, doc: dict, items: list[dict]) -> None:
    fname = doc["__file"]
    ids = {i["id"] for i in items}

    # quantity 0 is only legal as a removal directive in a child template
    if not doc.get("extends"):
        for i in doc.get("items", []):
            if i.get("quantity") == 0:
                errors.append(
                    f"{fname}: item '{i['id']}' has quantity 0 in a base template; "
                    "0 is only meaningful as a removal in a child"
                )

    # substitutes must point at real items in the resolved set
    for i in items:
        for sub in i.get("substitutes", []):
            if sub not in ids:
                errors.append(
                    f"{fname}: item '{i['id']}' lists substitute '{sub}' which does not exist"
                )
        if sub_self := (i["id"] in i.get("substitutes", [])):
            errors.append(f"{fname}: item '{i['id']}' lists itself as a substitute")

    # a redundancy group with one member is a modelling mistake, not an error
    groups: dict[str, list[str]] = {}
    for i in items:
        if g := i.get("redundancy_group"):
            groups.setdefault(g, []).append(i["id"])
    for g, members in groups.items():
        if len(members) < 2:
            warnings.append(
                f"{fname}: redundancy_group '{g}' has only one member ({members[0]}); "
                "groups exist to express alternative means to one capability"
            )

    # edc_tier is only meaningful on the self layer
    if "edc_tier" in doc and doc.get("layer") != "self":
        errors.append(f"{fname}: edc_tier set but layer is '{doc.get('layer')}', not 'self'")

    # estimated pack weight against a declared ceiling
    ceiling = (doc.get("container") or {}).get("target_weight_kg")
    if ceiling:
        total_g = 0.0
        unknown = []
        for i in items:
            w = i.get("weight_g")
            if w is None:
                if i.get("criticality") != "optional":
                    unknown.append(i["id"])
                continue
            qty = i.get("quantity", 0)
            # only fixed-scaling lines are meaningful without a household profile
            if i.get("scaling", "fixed") == "fixed":
                total_g += w * (qty if i.get("unit") in ("ea", "pair", "set") else 1)
            else:
                total_g += w
        total_g += (doc.get("container") or {}).get("weight_g", 0) or 0
        kg = total_g / 1000
        status = "OVER" if kg > ceiling else "ok"
        print(f"    weight estimate: {kg:.2f} kg vs ceiling {ceiling} kg [{status}]")
        if kg > ceiling:
            warnings.append(
                f"{fname}: estimated weight {kg:.2f} kg exceeds declared "
                f"target_weight_kg of {ceiling} kg"
            )
        if unknown:
            warnings.append(
                f"{fname}: {len(unknown)} non-optional items lack weight_g, so the "
                f"estimate is a floor: {', '.join(unknown[:5])}"
                + (" ..." if len(unknown) > 5 else "")
            )

    # consumables should say how they are checked
    for i in items:
        c = i.get("consumable")
        if not c:
            continue
        if not c.get("shelf_life_months") and not c.get("check_interval_months"):
            warnings.append(
                f"{fname}: item '{i['id']}' is consumable but declares neither "
                "shelf_life_months nor check_interval_months, so nothing will remind you"
            )
        if c.get("degrades_without_expiry") and not c.get("check_interval_months"):
            errors.append(
                f"{fname}: item '{i['id']}' degrades_without_expiry but has no "
                "check_interval_months; there is no other way to surface it"
            )


def main() -> int:
    tdir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "templates"
    templates = load_templates(tdir)
    print(f"Loaded {len(templates)} template(s) from {tdir}\n")

    check_schema(templates)

    for tid, doc in templates.items():
        print(f"  {doc['__file']}  ({tid})")
        items = resolve(tid, templates)
        base = len(doc.get("items", []))
        if doc.get("extends"):
            print(f"    extends {doc['extends']}: {base} own lines -> {len(items)} resolved")
        else:
            print(f"    {len(items)} items")
        check_cross_field(tid, doc, items)
        ess = sum(1 for i in items if i.get("criticality") == "essential")
        cons = sum(1 for i in items if i.get("consumable"))
        print(f"    {ess} essential, {cons} consumable")
        print()

    if warnings:
        print(f"{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  ! {w}")
        print()

    if errors:
        print(f"{len(errors)} error(s):")
        for e in errors:
            print(f"  x {e}")
        return 1

    print("All templates valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
