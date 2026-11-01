# Disclaimer

**This project provides organizational tooling, not emergency guidance.**

The templates in this repository describe generic categories of supplies. They
are a starting structure for organizing your own planning. They are not
professional emergency management, medical, or safety advice, and they have not
been reviewed or endorsed by any emergency management agency.

## Specifically

**A readiness score is not a safety measure.** It measures conformance to a
template someone wrote. A kit scoring 100% may still be wrong for your household,
your region, your climate, or the specific hazards you actually face.

**Templates are sized for stated assumptions.** Every template declares an
`assumptions` block. A template sized for one temperate-climate adult is not
correct for a cold-climate household of five, and rescaling it by headcount does
not make it correct. Read the assumptions before relying on a template.

**Medication planning requires a clinician.** Templates reference maintaining a
reserve of prescription medication. How, or whether, that is possible depends on
your prescription, your prescriber, your insurer, and your jurisdiction. Discuss
it with the prescribing clinician. Do not build a reserve by skipping doses.

**Some items are legally restricted.** Blade length, locking mechanisms,
chemical sprays, and radio transmit privileges vary considerably between
jurisdictions, and workplace policy may be stricter than local law. The
`regulatory_note` field flags common cases, but it is not comprehensive and is
not legal advice. Verify what applies where you live.

**Skills matter more than supplies.** Templates declare a `skills` block for a
reason. Gear you cannot use is weight. Water treatment, bleeding control, and
utility shutoff all require practice before the event, not during it.

**Follow official guidance during an actual emergency.** Local emergency
management, public health authorities, and first responders have information
about the specific situation that no static template can. If their instructions
conflict with anything here, follow them.

## Data security

Read `docs/threat-model.md` before deploying any implementation of this spec. A
populated instance contains an indexed inventory of household valuables, identity
documents, and household composition. The security requirements in that document
are requirements, not suggestions.

## No warranty

This specification and its templates are provided as-is under CC0-1.0, without
warranty of any kind. See `LICENSE`.
