# SignalDesk — Trainable request triage with human review

**Category:** AI Automation  
**Provenance:** New independent software project, September 2026  
**Project owner:** Ismail Habib  
**Status:** Functional local application; not a deployed client engagement

## The problem

Small teams often route repetitive requests by reading each message manually. SignalDesk turns labeled examples into a local statistical classifier, while keeping people in charge of the final decision.

## What was built

The web interface accepts labeled requests one at a time or through CSV. A multinomial Naive Bayes model learns category word distributions. Each new request produces a proposed category, relative scores, vocabulary coverage, and an inspectable set of matched terms. Low-overlap inputs are flagged for review instead of silently receiving a confident route. Human confirmations are stored beside the original suggestion and become learning examples. Current reviews are combined with curated examples without deleting their provenance; revising one request cannot erase another request’s feedback or an imported example. The queue exports to CSV.

## Delivered capabilities

- CSV import with required-column validation and duplicate handling
- Trainable text classification using real user-provided categories
- Abstention for unknown vocabulary and sparse overlap
- Human correction, persistent SQLite history, and CSV export
- Local-only HTTP interface with Host/Origin checks and bounded inputs

## Verification

Thirteen behavioral tests passed: six classifier checks, five persistence/export regressions, and two request-body boundary checks. Coverage includes unknown-vocabulary abstention, category selection, score normalization, Unicode, correction provenance, independent reviews of identical text, consistent training counts, empty CSV review fields, and multibyte document payloads. Local HTTP checks verified training import, classification, human feedback, CSV export, origin rejection and unknown-route errors. A browser interaction classified a separate request as Sales and confirmed it in the review queue. The screenshot dataset is a small, explicitly labeled verification fixture; these results do not measure real-world model accuracy.

## Scope and limitations

Scores are not calibrated probabilities. The included dataset is for functional verification, not a trained business model. A deployment should use representative business examples and a separate held-out evaluation set. This version is a single-user local tool with no authentication, cloud hosting, email ingestion, or automatic downstream actions.

## Screenshots

![The running classifier routes a verification request and displays category scores and matched vocabulary.](screenshots/01-classification.png)

The running classifier routes a verification request and displays category scores and matched vocabulary.

![The persistent decision queue preserves original suggestions and human confirmations.](screenshots/02-human-review.png)

The persistent decision queue preserves original suggestions and human confirmations.
