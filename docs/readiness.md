# Readiness scoring

Every inventory tool tells you what you have. The point of scoring a real kit
against a template is to tell you what you are **missing**, and to do it in a way
that does not quietly mislead.

This document specifies the algorithm so that two implementations produce the same
number for the same data.

## Scaling

Before comparison, resolve each template item's target quantity against the
household profile:

| `scaling`             | Multiplier                                    |
|-----------------------|-----------------------------------------------|
| `fixed`               | 1                                             |
| `per_person`          | number of persons                             |
| `per_person_per_day`  | persons x days in the kit's `duration`         |
| `per_pet`             | number of pets                                |
| `per_vehicle`         | 1 per vehicle the kit is assigned to           |
| `per_household`       | 1                                             |

Duration in days: `72h` = 3, `2w` = 14, `1m` = 30, `3m` = 90, `1y` = 365.
`indefinite` has no defined multiplier; treat `per_person_per_day` lines in an
indefinite kit as unscored and say so, rather than inventing a number.

If the household profile differs materially from the template's `assumptions`
(different climate, different mobility), surface a warning alongside the score.
Silently rescaling a temperate template for an arctic household produces a
confident number that is wrong.

## Per-item coverage

For each resolved template item, sum the quantity of user items whose
`template_item_id` matches, counting only **valid** stock:

- Lots with `status` of `consumed`, `discarded`, or `rotated_out` never count.
- Lots past their `expires` date do not count toward coverage, but are reported
  separately as expired rather than silently vanishing. A user with expired water
  is in a different situation from one with no water, and the report must say which.
- Items with `archived: true` do not count.

Coverage ratio is `min(1.0, valid_quantity / scaled_target)`.

If the item is unsatisfied and lists `substitutes`, check them before declaring a
gap. A satisfied substitute counts the item as covered. Do not double-count: an
item and its substitute together contribute at most 1.0.

## Aggregation, and the rule that matters most

**Never produce a single percentage by averaging across criticality levels.**

A kit with every optional item and no water scores well under naive averaging,
and that number is worse than no number at all, because it produces false
confidence in exactly the situation where confidence is most costly.

Report three separate figures:

```
essential:   9 / 12 covered   (75%)
recommended: 6 / 10 covered   (60%)
optional:    2 / 6  covered   (33%)
```

If a single headline figure is required for a dashboard, use the **essential
ratio alone** and label it as such. Recommended and optional coverage may modify
presentation but must never raise the headline number above essential coverage.

A kit with any uncovered essential item is reported as **incomplete**, regardless
of its percentages.

## Redundancy groups

Items sharing a `redundancy_group` serve one capability by different means. Report
capability coverage alongside item coverage: a group with at least one covered
member is a covered capability, and a group where every member is covered is
noted as redundant.

Do not collapse group members into a single scored item. The user asked for two
means to make light; a report that says "lighting: covered" when only the pocket
flashlight is present has discarded the specific thing the group was expressing.

## Freshness

Coverage is not readiness. Report these separately:

- **Expiring soon** — lots with `expires` inside a configurable horizon
  (default 90 days).
- **Expired** — past `expires`, still physically present. Called out distinctly
  from missing.
- **Check overdue** — `next_check` in the past, or an item whose consumable
  profile sets `check_interval_months` with no maintenance event inside that
  window. This is the only mechanism that catches `degrades_without_expiry`
  items, which is why the schema requires an interval whenever that flag is set.
- **Unverified** — `kit.last_verified` older than a configurable interval
  (default 12 months). A kit whose record has drifted from the physical bag is
  the most common real failure, and one no amount of accurate data entry prevents.

A kit at 100% coverage that has not been physically opened in three years should
not display as ready. Weight `last_verified` prominently.

## Weight

Where a template declares `container.target_weight_kg`, sum `weight_g` across
covered user items (falling back to template estimates where a user item has no
weight) and compare. Report the estimate as a floor when any non-optional item
lacks a weight, since a partial sum that looks comfortably under the ceiling is
misleading.

Flag exceeding the ceiling. An unliftable bag is a failed bag, and this is a
failure mode that pure item-count scoring is structurally blind to.

## What not to do

- Do not gamify. Streaks, badges, and completion pressure encourage buying gear
  over building skill, and gear without skill is the failure this domain is
  already worst at.
- Do not present a score as a safety guarantee. It measures conformance to a
  template someone wrote, nothing more. Say so in the UI.
- Do not let AI-generated suggestions write directly into readiness state. Gap
  analysis is advisory and belongs beside the score, never inside it.
