# PrepKit Spec (v0.1 draft)

A portable, vendor-neutral format for describing emergency preparedness kits, and
the data model for an application that tracks real holdings against them.

This repository is **specification and data only**. No application code lives
here, deliberately: the format should outlive any one implementation, and a
format with a reference implementation attached tends to drift toward whatever
that implementation happens to do.

## Why a spec first

The hard part of this problem is not CRUD. It is agreeing on what a kit *is* in a
way that survives contact with real households, real expiration dates, and real
disagreement about what belongs in a bag. If the format is right, templates can
be contributed by people who will never write code, which is the only realistic
way this ever covers more than a handful of kits.

## Contents

```
schema/
  kit-template.schema.json   Template format: an aspirational standard
  inventory.schema.json      Runtime entities: what a user actually owns
templates/
  home-72hr-baseline.yaml    Shelter-in-place, 72 hours
  get-home-bag-urban.yaml    On-foot return, weight-constrained
  vehicle-kit-baseline.yaml  Extends the get-home bag; demonstrates inheritance
docs/
  categories.md              Category taxonomy and color mapping
  readiness.md               Scoring algorithm
  licensing.md               Rules for derived templates. Read before contributing.
  threat-model.md            Data sensitivity. Read before writing storage code.
validate.py                  Schema and cross-field validator, CI-safe
CLAUDE-CODE-PROMPT.md        Phase 1 build brief for an AI coding agent
DISCLAIMER.md                Scope limits. Read this one too.
.github/workflows/           CI: validates templates and confirms the validator
                             still rejects known-bad input
```

## The two schemas, and why they are separate

A **template** is a standard: generic item types and target quantities, written
once and shared. `folding knife, quantity 1, essential`.

An **inventory** is a user's reality: the specific knife they own, in a specific
pouch, with a specific purchase date. It carries a `template_item_id` pointing
back at the line it satisfies.

Keeping them separate is what makes template upgrades non-destructive. Your knife
stays yours when the template revises its knife line, because the link is by
stable id rather than by name matching.

## The Item / Lot split

The most consequential modelling decision here, and the one most inventory tools
get wrong.

- **Item**: a type of thing you own. "Canned chili."
- **Lot**: a dated batch of it. "Six cans, best-by 2027-03." And separately,
  "four cans, best-by 2029-08."

Expiration lives on lots. Collapsing the two makes partial rotation
unrepresentable: you cannot eat the older half of your stock and record it
without either losing the date or inventing a duplicate item. Grocy gets this
right, and it is why expiration tracking works there and fails in most home
inventory tools.

Non-expiring items carry quantity directly and have no lots.

## Kit structure

Templates locate a kit in a concentric model of preparedness layers, from
`self` (carried on the body) outward through `home`, `vehicle`, `offsite`, and
`evacuation`. Home-base kits additionally carry a `duration` tier (72h through
indefinite), and evacuation kits carry a tier from short-term displacement
through long-term relocation.

This framing is a widely used organizing model in the preparedness community
rather than anything invented here, and it was adopted because it is the
vocabulary the intended users already speak. Frameworks and systems are freely
implementable; specific published kit lists are not. See `docs/licensing.md`.

## Validation

```
pip install jsonschema pyyaml
python3 validate.py
```

Checks JSON Schema conformance, resolves `extends` chains, verifies merge-key and
substitute referential integrity, estimates pack weight against declared
ceilings, and flags consumables that declare no way to be checked. Exits nonzero
on failure.

The validator earns its keep: it caught two real modelling gaps in the seed
templates on first run, both of which would have produced a consumable that
silently never surfaces a reminder.

## Inheritance

`extends` merges item lists by `item.id`. A child entry with a matching id
overrides the parent's; a child entry with `quantity: 0` removes it. Single
inheritance, maximum depth 3.

`vehicle-kit-baseline` demonstrates the pattern: it extends the get-home bag on
the reasoning that a vehicle kit should *contain* a get-home bag rather than
duplicate one, then overrides the lines where the vehicle context genuinely
changes the answer. Weight ceilings disappear, so water quantity rises; heat
cycling in a parked car destroys consumables, so check intervals drop sharply.

## Design constraints

**Templates are pure data.** No scripting hooks, no expressions, no executable
content, ever. Packs are contributed by strangers and this is the property that
makes that safe.

**Colors are presentation.** Templates declare a functional `category`;
consumers map to color at display time. Palettes vary between communities, and a
template written against one should not be wrong under another.

**Nothing is a safety guarantee.** A readiness score measures conformance to a
template someone wrote. Implementations must say so where users can see it.

## Scope and safety

Read `DISCLAIMER.md`. In short: this is organizational tooling, not emergency
guidance. A readiness score measures conformance to a template someone wrote,
nothing more, and implementations must say so where users can see it.

## Status

Draft. The format has been exercised against three templates spanning three
layers, one inheritance chain, and both scaling and weight-ceiling logic. It has
not been exercised against a real application, a real household, or a contributor
who is not its author. All three will find problems.

Breaking changes are expected before 1.0 and will bump `spec_version`.

## Contributing templates

1. Read `docs/licensing.md`. Every template needs a `source` block with a license.
2. Generic item types only. Product picks belong in `exemplars`, which is
   advisory and omitted by default in redistributed packs.
3. Run `validate.py` before opening a pull request.
4. State your `assumptions`. A template that does not say what it was sized for
   cannot be safely rescaled by anyone else.
