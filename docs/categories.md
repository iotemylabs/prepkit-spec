# Categories and color coding

## Why colors are presentation, not data

A widely used convention in the prepping community assigns a color to each
functional category, so a shelf of pouches can be read at a glance. The convention
is genuinely useful and this spec supports it, but the color is deliberately kept
out of the template item schema.

Two reasons. First, conventions vary: not everyone uses the same palette, and a
template written against one palette should not be wrong under another. Second,
the color of the pouch a user actually owns is a fact about their physical
storage, not about the item's function, which is why `container.color_code` lives
on the runtime container entity where it can hold whatever color the real pouch
is.

Templates declare `category`. Consumers map category to color at display time.

## Canonical mapping

The eleven colored categories follow the common convention:

| Category     | Color  | Covers                                              |
|--------------|--------|-----------------------------------------------------|
| `water`      | blue   | Storage, treatment, filtration, containers          |
| `food`       | green  | Stored food, rations, supplements, pet food         |
| `shelter`    | brown  | Tarps, bivvies, blankets, sheeting, cordage         |
| `first_aid`  | red    | Medical supplies, medication, trauma gear           |
| `comms`      | yellow | Radios, signaling, contact lists, written plans      |
| `fire`       | orange | Ignition sources, tinder, fuel                      |
| `tools`      | black  | Cutting, repair, prying, general utility            |
| `hygiene`    | white  | Sanitation, washing, waste management               |
| `clothing`   | purple | Garments, footwear, PPE, respirators                |
| `personal`   | pink   | Cash, comfort items, entertainment, individual needs |
| `cooking`    | gray   | Stoves, cookware, utensils, openers                 |

## The four additions

This spec adds four categories that the eleven-color convention folds elsewhere.
Each is added because folding it made a real reporting problem worse, and none has
an assigned color; consumers should render them neutrally or extend the palette.

- **`power`** — lights, batteries, power banks, generators, charging. Usually
  folded into comms or tools. Separated because power items share a distinctive
  failure mode: they self-discharge and degrade on a schedule unrelated to
  anything printed on them, and a rotation dashboard is much more useful when it
  can address them as a class.

- **`documents`** — identity, insurance, medical records, written plans.
  Separated because this is the category with a completely different security
  posture from everything else in the model. Everything here is sensitive by
  default and must be handled accordingly on export.

- **`navigation`** — maps, compass, route plans. Usually folded into comms.
  Separated because navigation items are among the few that go stale by revision
  rather than by expiry, and because a get-home kit's readiness depends on them
  specifically.

- **`security`** — extinguishers, alarms, signaling for hazard, defensive items.
  Separated so a consumer can filter or hide the category wholesale. Legal
  restrictions here vary enormously by jurisdiction, and the `regulatory_note`
  field on template items exists largely for this category and for blades.

## Guidance on choosing a category

Categorize by **function in use**, not by material or by where it is stored. A
metal water bottle is `water`, not `tools`. A lighter is `fire` even if it lives
in the tool pouch. A written contact list is `comms` because its function is
communication, while a passport copy is `documents` because its function is proof
of identity.

When an item genuinely serves two functions, pick the one that would make you
notice its absence, and use `redundancy_group` to express the other relationship.
