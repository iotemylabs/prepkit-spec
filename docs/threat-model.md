# Threat model and data sensitivity

Write this down before Phase 2, not after. The document vault turns this project
from an inventory app into a store of exactly the material an attacker most wants,
and the offline export feature deliberately copies that material onto devices that
leave the house.

## What the data is

A fully populated instance holds:

- A complete inventory of household valuables, with serial numbers and purchase
  costs, indexed by location within the home.
- Identity, insurance, medical, and financial documents.
- Household composition, including children and anyone with a dependency or
  mobility need.
- Where the household goes when it leaves, and when it will not be home.

That combination is more useful to a burglar than a burglary, and more useful to
a stalker than either. Treat it accordingly.

## Realistic adversaries, in priority order

1. **Opportunistic network attacker.** The dominant real risk. Someone finds the
   instance because it was exposed to the internet, directly or through a
   misconfigured tunnel. Mitigation: bind to LAN by default, ship no default
   credentials, refuse to start with an unset admin secret, and warn loudly on any
   configuration that binds a public interface.

2. **Device theft.** The e-ink export device, a phone, or the server itself is
   taken. This is the threat the export feature creates and the reason exports are
   opt-in per document rather than a single switch. Mitigation: encryption at
   rest for the document vault, and exports that default to excluding every
   sensitive field.

3. **Household insider and shared access.** Multi-user households where not
   everyone should see everything. Deferred, but do not design a schema that makes
   per-document access control impossible to add later.

4. **Supply chain.** A malicious template pack or container image. Mitigation:
   templates are declarative data with no executable content by design, which is
   a deliberate constraint on the format. Never add a scripting hook to the
   template spec.

Explicitly **out of scope**: a targeted, resourced adversary. Say so plainly in
user-facing documentation rather than implying protection the project does not
provide.

## Field classification

The schemas mark these as sensitive. Implementations must honor the marks.

**Never in an unencrypted export, no exception:**
- Everything under `document` where `kind` is `identity`, `financial`,
  `insurance`, or `medical`
- `person.needs`
- `item.serial`

**Excluded from export by default, opt-in per export:**
- `item.cost`
- `person.label` where it is a full legal name
- `container.location_note`
- Any `document` regardless of kind, gated on its own `export_ok` flag

**Ordinary:**
- Item names, categories, quantities, expiration dates
- Kit structure and readiness figures
- Template content

## Rules for implementations

1. **`export_ok` defaults to false and there is no bulk override.** A single
   "export everything" switch defeats the entire mechanism. Per-document consent
   or nothing.

2. **The offline export is plain, script-free HTML.** No JavaScript, no network
   requests, no analytics. It must render on a decade-old e-reader and must not
   be capable of phoning anywhere.

3. **Encrypt the document vault at rest,** with a key derived from a passphrase
   that is not the login password. A vault that unlocks whenever the app runs is
   not encrypted in any sense that matters for device theft.

4. **QR slugs are opaque local tokens.** Never encode a URL containing personal
   data, an address, or anything resolvable off-instance. A label on a bin in a
   garage is a public object.

5. **Log nothing sensitive.** Not in application logs, not in error traces, not in
   crash reports. Redact by field classification, not by pattern matching.

6. **Never phone home.** No telemetry, no update pings carrying instance data, no
   crash reporting by default. The user base for this application selected for
   distrust of exactly that, and correctly.

## AI-specific constraints

Once a local model is in the loop, restate these:

- **Never send inventory or document content to a remote endpoint.** If a user
  configures a hosted API rather than a local one, warn explicitly and require
  confirmation, every time, naming what would leave the machine.
- **Exclude the document vault from any RAG index by default.** Opt-in per
  document, reusing the same consent mechanism as export.
- **Ground medical and structural advice in retrieved documents or refuse.** A
  fluent, confident, wrong answer about wound care or water potability during an
  actual emergency is the most serious harm this project could plausibly cause.
  Cite the source or decline; do not free-generate in these categories.
- **AI output never writes to readiness state.** Suggestions are advisory,
  presented as such, and require an explicit user action to become data.
