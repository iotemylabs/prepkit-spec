# Licensing and attribution for templates

Read this before writing a template derived from anyone else's published work.
This is the single largest legal risk in the project, and getting it wrong once
in a distributed pack is much harder to undo than getting it right the first time.

None of what follows is legal advice. It is the working policy for this repo.

## The distinction that matters

A **system** is not copyrightable. Organizing preparedness into concentric layers,
scoring sustainment in duration tiers, assigning colors to functional categories,
splitting EDC into tiers by pocket space: these are methods and ideas. You may
implement them freely, and this spec does.

A **curated list** generally is protected. A specific author's selection of items,
their arrangement, their commentary, and their exact wording represent creative
effort. Reproducing "his bug-out bag list" as a template file, even reworded and
even with credit, copies the thing the effort actually went into.

The practical line for this repo:

| Safe to implement                              | Not safe to copy                                |
|------------------------------------------------|-------------------------------------------------|
| A layered/concentric organizing model           | A named author's kit list reproduced as a template |
| Duration tiers (72h / 2w / 1m / 3m / 1y)        | Their per-item quantities, weights, and costs as published |
| A color-coded category taxonomy                 | Their prose descriptions or notes, copied or lightly reworded |
| Generic item types ("folding knife")            | Their specific product picks presented as the list |
| Publicly stated planning figures                | Their PDFs, spreadsheets, or video content, redistributed |

## Rules for this repository

1. **Every template declares a `source` block.** No license, no merge.
2. **Templates name generic item types, never products.** `exemplars` exists for
   products, is advisory, and is omitted by default in redistributed packs.
3. **`derived_from` is required whenever a template was informed by identifiable
   third-party material,** even loosely. Cite it and describe the relationship.
4. **`permission_status: unverified` combined with a `derived_from` value will not
   be distributed.** Resolve it to `original`, `public_domain`, `licensed`, or
   `permission_granted` first.
5. **No template is named after a person or channel without written permission.**
   Not the filename, not the `name`, not the `id`, not the tags. "Urban Get-Home
   Bag" is fine. "TheUrbanPrepper's Get-Home Bag" requires a yes in writing.

## If you want to ship an author-specific pack

The right sequence, in order:

1. Ask. Email or use the contact form, describe the project, state that it is
   open source and non-commercial, and be specific about what you want to include
   and how it will be attributed.
2. Get the answer in writing and keep it.
3. Publish it as a **separate, opt-in pack**, not in the core template set.
4. Set `permission_status: permission_granted` and put the grant details in
   `derived_from`.
5. Honor withdrawal immediately if asked, and design pack loading so removal is
   a one-file deletion rather than a code change.

Many creators in this space are receptive; several explicitly encourage adapting
their systems. Cliff Colon of The Urban Prepper has described treating his
large-scale kits as open-source projects viewers can adapt, which is an
encouraging signal but is not itself a license. Ask anyway. A short email is
cheaper than a takedown, and a public "used with permission" is worth more to the
project than anything you would get from not asking.

## Safe sources for building out the corpus

- **US government emergency preparedness guidance.** US federal works are
  generally not subject to domestic copyright, which makes agency preparedness
  material a solid foundation for baseline templates. Verify the specific
  document rather than assuming.
- **Public-domain military field manuals.** Already circulating in this ecosystem
  as offline content packs, and a good source for skills references.
- **Your own kits.** The most defensible source there is, and often the most
  useful, because it is real rather than aspirational.
- **Convergent public guidance.** Where many independent public sources state the
  same planning figure, that figure is a fact about consensus practice, not
  anyone's creative expression.

## Recommended license for contributed templates

**CC0-1.0** for templates. The point of this format is that packs travel freely
and get remixed for local conditions; attribution requirements create friction
that mostly harms adoption. Contributors preferring credit may use CC-BY-4.0.
The schema itself and the reference implementation carry their own license, noted
at the repo root.
