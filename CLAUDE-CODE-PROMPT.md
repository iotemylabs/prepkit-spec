# PrepKit — Claude Code Master Prompt

Paste this as the opening message of a Claude Code session, with the
`prepkit-spec/` directory present in the working tree. It assumes the Phase 0
artifacts (`schema/`, `templates/`, `docs/`, `validate.py`) already exist and are
authoritative.

Everything below the line is the prompt.

---

## Project

You are building **PrepKit**, a self-hostable emergency preparedness manager. It
tracks preparedness kits, the items in them, and the expiration dates of the
consumables inside them, then scores real holdings against reusable kit
templates to tell the user what they are *missing*.

This is a standalone application. It does not depend on Grocy, Homebox, Mealie,
Home Assistant, or Project NOMAD, though optional adapters for those are planned
for a later phase and the architecture should not preclude them.

The primary consumer is the **web UI**. A secondary consumer is an **offline
export** rendered as plain static HTML for e-ink devices (Kindle, BOOX) or for
serving from a low-power always-offline node such as a Raspberry Pi.

## Read these first, before writing any code

The specification is already written and is authoritative. Read all of it before
you start:

| File | What it governs |
|---|---|
| `README.md` | Overall model, the Item/Lot split, design constraints |
| `schema/kit-template.schema.json` | Template format (the aspirational standard) |
| `schema/inventory.schema.json` | Runtime entities (what the user actually owns) |
| `docs/readiness.md` | Scoring algorithm — implement exactly as specified |
| `docs/threat-model.md` | Data sensitivity — read before writing storage code |
| `docs/categories.md` | Category taxonomy and color mapping |
| `docs/licensing.md` | Rules for template provenance |
| `templates/*.yaml` | Three worked examples spanning three layers |
| `validate.py` | Existing validator; keep it passing |

If the spec and this prompt appear to disagree, **the spec wins**. If the spec is
genuinely ambiguous, stop and ask rather than guessing — the ambiguity is a bug
in the spec worth fixing at the source.

## Phase 1 scope

Build only this. Later phases are listed at the end for context, not for
implementation.

1. Load and validate template packs from disk at startup
2. Instantiate a template into a real kit, scaled against a household profile
3. CRUD for kits, containers, items, and lots
4. Expiration and rotation dashboard
5. Readiness scoring per `docs/readiness.md`
6. QR label generation for containers
7. Full JSON export conforming to `inventory.schema.json`
8. Static offline HTML export

Explicitly **out of scope for Phase 1**: AI features, mobile sync, third-party
adapters, multi-user accounts, the encrypted document vault.

## Stack

- **Go 1.22+**, single binary, embedded web UI via `embed.FS`
- **SQLite** via `modernc.org/sqlite` (pure Go, no cgo, so cross-compilation for
  ARM targets stays trivial — a Raspberry Pi is a first-class deployment target)
- **No frontend build step.** Server-rendered HTML with progressive enhancement.
  htmx is acceptable. A React/Vite/Node toolchain is not.
- **One Docker image**, one container, no sidecars, no external database
- Standard library `net/http` and `html/template` preferred over frameworks

The single-binary constraint is deliberate and non-negotiable. The target user
runs this on hardware they expect to still boot in five years, in a scenario
where they cannot download a missing dependency.

## Architecture

```
cmd/prepkit/main.go        entrypoint, flag parsing, graceful shutdown
internal/model/            entities mirroring inventory.schema.json
internal/store/            SQLite persistence, migrations
internal/template/         pack loading, extends resolution, validation
internal/readiness/        scoring engine (pure functions, no I/O)
internal/export/           JSON export + static HTML generator
internal/web/              handlers, embedded templates and assets
templates/                 bundled template packs (embedded)
migrations/                numbered .sql files, embedded
```

Keep `internal/readiness` free of database and HTTP dependencies. It takes
resolved templates plus inventory structs and returns a report. That makes it
directly testable against fixtures, which matters because it is the component
most likely to harbor subtle errors.

## Data model notes

Mirror `inventory.schema.json`. Three points deserve emphasis because they are
where implementations typically go wrong:

**The Item/Lot split is load-bearing.** An Item is a type of thing owned
("canned chili"). A Lot is a dated batch of it ("six cans, best-by 2027-03").
Expiration lives on Lots. Multiple lots per item is the normal case, not an edge
case — it is how partial rotation is represented. When an item has lots, its own
`quantity` column must be null and the effective quantity derived by summing
lots, so the two can never disagree.

**`template_item_id` is the link that survives upgrades.** A user's specific
knife points at the template's generic `folding-knife` line by stable id, not by
name matching. Revising the template's wording must not orphan the user's item.

**Containers nest.** A pouch inside a pack inside a vehicle is three containers
and two parent edges. Reject self-referential and cyclic parentage on write, not
just at read time.

Use `TEXT` for UUIDs and ISO-8601 dates. Do not use SQLite's date functions for
business logic; parse in Go where the timezone handling is explicit.

## Template loading

Implement `extends` resolution exactly as `validate.py` does, and port its
cross-field checks into Go so the server rejects bad packs at startup rather
than failing mysteriously later:

- Merge parent and child item lists by `item.id`
- A child entry with a matching id overrides the parent's
- A child entry with `quantity: 0` removes the inherited line
- Single inheritance, maximum depth 3
- `quantity: 0` in a base template is an error, not a removal
- `substitutes` must reference items that exist in the resolved set
- `degrades_without_expiry` without `check_interval_months` is an error
- A template with no `source.license` must not load

`templates/vehicle-kit-baseline.yaml` extends `get-home-bag-urban` and resolves
21 own lines to 41. Use that as your integration fixture — if your resolver
produces any other count, it is wrong.

Add a `prepkit validate` subcommand that runs these checks from the CLI and
exits nonzero on failure, so pack authors get the same feedback the server does.

## Readiness scoring

Implement `docs/readiness.md` precisely. The rules most likely to be
"simplified" into wrongness:

- **Never average across criticality levels into one percentage.** Report
  essential, recommended, and optional coverage as three separate figures. A kit
  with every optional item and no water must not display as well-prepared.
- Any uncovered essential item marks the kit **incomplete**, regardless of
  percentages.
- If a single headline number is needed, it is the essential ratio alone, and
  labeled as such. Recommended and optional coverage may never raise it.
- Expired lots do not count toward coverage but are reported **separately** from
  missing. "Expired water" and "no water" are different situations and the report
  must distinguish them.
- Check `substitutes` before declaring a gap; an item and its substitute together
  contribute at most 1.0.
- Report redundancy-group capability coverage alongside item coverage. Do not
  collapse group members into one scored line.
- Surface `last_verified` prominently. A kit at 100% coverage that has not been
  physically opened in three years is not ready, and no amount of accurate data
  entry changes that.

Scaling multipliers and duration-to-days mapping are in the doc. `indefinite`
has no defined day count — leave `per_person_per_day` lines in an indefinite kit
unscored and say so in the report rather than inventing a number.

If the household profile materially differs from the template's `assumptions`
(different climate, different mobility), attach a warning to the report.
Silently rescaling a temperate template for an arctic household produces a
confident wrong answer.

## Security requirements

Read `docs/threat-model.md` in full. These are requirements, not suggestions:

- **Bind to localhost by default.** Binding a public interface requires an
  explicit flag and prints a loud warning.
- **No default credentials.** Refuse to start if an admin secret is unset.
- **`export_ok` defaults to false, and there is no bulk override.** A single
  "export everything" switch defeats the mechanism entirely. Per-document
  consent or nothing.
- **The static export contains no JavaScript**, no external requests, no
  analytics. It must render on a decade-old e-reader and must be structurally
  incapable of phoning anywhere.
- **QR slugs are opaque local tokens.** Never encode a URL containing personal
  data or anything resolvable off-instance. A label on a bin in a garage is a
  public object.
- **Never phone home.** No telemetry, no update pings, no crash reporting. This
  user base selected for distrust of exactly that, and they were right to.
- **Redact by field classification in logs**, not by pattern matching. `item.serial`,
  `person.needs`, `item.cost`, and all document bodies never reach a log line.

A populated instance is an indexed inventory of household valuables with serial
numbers, plus identity documents, plus a schedule of when the house is empty.
That is more useful to a burglar than a burglary. Build accordingly.

## Offline export

Generate a self-contained directory of static HTML: no JS, no external CSS, no
web fonts, inline styles only, semantic markup, high contrast, large default
type. Assume a 6-inch 800x600 greyscale e-ink display with slow refresh and no
scripting.

Structure: index → kit list → per-kit manifest → contact sheet → plans. Every
page reachable within two taps of the index, since e-ink navigation is painful.

Sensitive fields are excluded by default per the threat model. A document
appears only if its own `export_ok` is true.

## Testing

- Table-driven unit tests for the readiness engine against JSON fixtures. This
  component gets the most coverage because it is where a subtle error produces a
  confidently wrong answer rather than a crash.
- Golden-file tests for the template resolver, including the 21→41 case.
- A round-trip test: export to JSON, reimport, confirm the result is identical.
- Negative tests for the validator. `validate.py` catches six distinct errors in
  a deliberately broken template; your Go port must catch the same six.
- A migration test that runs every migration against an empty database and then
  against a populated one.

## Working style

- **Commit incrementally** with clear messages. Do not produce one enormous
  commit at the end.
- **Run `validate.py` after touching anything in `templates/`.** Keep it passing.
- **Ask before deviating from the spec.** If an approach in `docs/` seems wrong,
  say so and explain why rather than silently implementing something else — you
  may well be right, and the spec should then be amended at the source.
- **Push back on scope creep**, including mine. If I ask for something that
  belongs in a later phase, say so.
- Prefer boring, obvious code. This is infrastructure someone may need to read
  and repair years from now, possibly under stress.
- Do not add dependencies without saying what each one buys and what it costs.

## Definition of done for Phase 1

- [ ] `docker run` produces a working instance with no external services
- [ ] The three bundled templates load, validate, and instantiate
- [ ] A user can create a household, instantiate a kit, add items and lots
- [ ] The expiration dashboard distinguishes expired, expiring, and check-overdue
- [ ] Readiness reports the three criticality figures separately, never averaged
- [ ] QR labels print and resolve to the right container
- [ ] JSON export validates against `inventory.schema.json`
- [ ] Static export renders correctly with JavaScript disabled entirely
- [ ] `prepkit validate` catches all six negative-test errors
- [ ] Binary cross-compiles for `linux/arm64` without cgo

## Later phases (context only — do not build)

- **Phase 2** — encrypted document vault, plans, review reminders
- **Phase 3** — optional Ollama integration for gap analysis and OCR intake;
  server-side only, strictly optional, never writing to readiness state, and
  refusing to free-generate medical or structural advice
- **Phase 4** — optional adapters for Homebox, Grocy, Home Assistant, and a
  Project NOMAD Supply Depot manifest
- **Phase 5** — offline-first Android client with sync

Design so these remain possible. Do not build toward them now.

## Start here

Read the spec files listed above, then propose a concrete implementation plan
covering the package layout, the SQLite schema with migrations, and the order
you intend to build in. **Wait for my approval before writing implementation
code.** If anything in the spec is ambiguous or looks wrong, raise it in that
first message.
