# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Primary:** Indian citizens—particularly senior citizens, smallholder farmers, students, job seekers, women heads-of-households, and daily-wage earners—seeking public welfare benefits, pensions, scholarships, and healthcare across Central and South Indian state programs (Karnataka, Andhra Pradesh, Tamil Nadu, Kerala).
- **Secondary:** Grassroots social workers, family caregivers, and village citizen center (CSC/Gram One) operators assisting non-English literate or elderly individuals in discovering statutory benefits and preparing mandatory documentation.

## Product Purpose

Sahayaka makes government welfare schemes transparent, discoverable, and actionable for every citizen. It bridges the gap between complex official gazettes and everyday citizens by allowing people to describe their personal situations in their native languages (English, Kannada, Telugu, Tamil, Malayalam) and immediately receive an honest, deterministic assessment of their eligibility, required document checklists, and verified application portals.

## Positioning

Unlike generic generative AI assistants that hallucinate administrative rules or guess eligibility, Sahayaka combines multilingual conversational entity extraction with a deterministic statutory evaluation engine. Sensitive demographic and financial attributes (such as disability status, BPL card ownership, or social category) are never guessed or inferred—they are verified against gazetted criteria rules or marked as pending.

## Operating Context

- **Environment:** High-stakes, bureaucratic, and often confusing public welfare administration where missing a single certificate or misinterpreting an income threshold results in rejected applications.
- **Linguistic Scene:** South Indian linguistic diversity with frequent code-mixing (English, Kannada, Telugu, Tamil, Malayalam, and Romanized script).
- **Privacy & Compliance:** Strict DPDP Act 2023 alignment. Personal profile data is retained purely in-memory for the active session, never stored permanently, tracked, or monetized.

## Capabilities and Constraints

### Capabilities
- **111 Verified Schemes:** Comprehensive Central and South Indian state schemes spanning Agriculture, Education, Social Welfare & Pensions, Employment & Business, Healthcare, and Women & Child Welfare.
- **Deterministic Rule Engine:** Explicit logic evaluating age boundaries, income ceilings, land ownership, domicile, occupation, education, and household conditions with transparent matching reasons.
- **Multilingual Support:** Native language conversational guidance across English, Kannada, Telugu, Tamil, and Malayalam.
- **Interactive Document Checklists:** Actionable document trackers (Aadhaar, land RTC, bank passbook, ration card) with live readiness indicators.
- **Printable Slips:** One-click offline document slips (`window.print()`) formatted for physical use at government counters.
- **Eligibility Ledger:** Split-pane desktop drawer (Claude Artifacts style) displaying collected profile attributes and matched schemes.

### Constraints
- **Advisory Only:** Sahayaka provides preliminary discovery and guidance; final eligibility determinations remain the exclusive jurisdiction of the relevant government departments.
- **Zero Hallucination / No Guessing:** Criteria with missing citizen attributes are flagged as unknown rather than assumed to pass.

## Brand Commitments

- **Name:** Sahayaka (`sahayaka.` — Sanskrit and Kannada for "helper" / "assistant").
- **Voice:** Dignified, polite, respectful public-service tone ("Namaskara", "Vanakkam", "Namaskaram"). Clear, empathetic, and free of bureaucratic jargon.
- **Visual Identity:** Warm, editorial Claude-inspired design system built on a warm parchment canvas (`#F4F1EA`), ivory conversation surface (`#F8F5EF`), stone sidebar (`#EEE9DF`), warm card tiles (`#F0EBE2`), and terracotta accent (`#B96F51`). Typography pairs `Cormorant Garamond` and `EB Garamond` display serifs with `Inter` and dedicated Indic fonts (`Noto Sans` Kannada, Telugu, Tamil, Malayalam). Clean Lucide outline icons replace multicolored emojis.

## Evidence on Hand

- **Scheme Definitions:** 111 verified JSON files at `data/schemes/` and compiled in `frontend-web/lib/policies.json`.
- **Database Seed:** `data/seed/verified_schemes.json`.
- **Test Suite:** 68 passing pytest tests (`tests/`) covering rule evaluation, entity extraction, concurrency, and API contracts.
- **NLP Evaluation Suite:** `scripts/evaluate_bilingual_nlp.py` achieving 100% precision, recall, and F1 across 12 bilingual test cases.

## Product Principles

1. **Zero Hallucination, Zero Guessing:** Statutory rules are evaluated strictly as written by official policy documents. Missing facts prompt follow-up questions, never guesses.
2. **Linguistic Parity & Dignity:** All 5 languages (English, Kannada, Telugu, Tamil, Malayalam) receive identical structural depth, polite address, and typographic clarity.
3. **Actionable Guidance Over Passive Information:** Every recommendation is paired with an interactive document checklist and verified portal link so citizens leave with a concrete action plan.
4. **Privacy by Design:** Strict adherence to the DPDP Act 2023; user profiles are session-scoped and never retained across restarts.

## Accessibility & Inclusion

- **Senior-Friendly Scaling:** In-app font switcher supporting normal (`A`), large (`A+`), and extra-large (`A++`) text sizing.
- **High-Contrast Warm Neutrals:** WCAG-compliant text contrast ratios across all surfaces without harsh pure white glare.
- **Keyboard & Screen Reader Support:** Semantic HTML, ARIA attributes, visible focus rings, and printable media styles.

