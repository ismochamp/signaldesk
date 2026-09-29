# Malt portfolio copy

## Title
SignalDesk — Trainable request triage with human review

## Short description
Small teams often route repetitive requests by reading each message manually. SignalDesk turns labeled examples into a local statistical classifier, while keeping people in charge of the final decision. The web interface accepts labeled requests one at a time or through CSV. A multinomial Naive Bayes model learns category word distributions. Each new request produces a proposed category, relative scores, vocabulary coverage, and an inspectable set of matched terms. Low-overlap inputs are flagged for review instead of silently receiving a confident route. Human confirmations are stored beside the original suggestion and become learning examples. The queue exports to CSV.

## Project type
Independent functional project. Local behavior verified on macOS; no client delivery or production deployment claimed.

## Skills
AI automation, Python, text classification, API integration, SQLite, web development

## Result
Thirteen automated tests passed, covering classification, feedback persistence, CSV export and request limits. Local HTTP checks verified training import, classification, human feedback, CSV export, origin rejection and unknown-route errors. A browser interaction classified a separate request as Sales and confirmed it in the review queue. The screenshot dataset is a small, explicitly labeled verification fixture; these results do not measure real-world model accuracy.

## Scope note
Scores are not calibrated probabilities. The included dataset is for functional verification, not a trained business model. A deployment should use representative business examples and a separate held-out evaluation set. This version is a single-user local tool with no authentication, cloud hosting, email ingestion, or automatic downstream actions.

## Suggested media order
1. First screenshot: working tool and primary result.
2. Second screenshot: review or source evidence.
3. `PORTFOLIO.pdf`: full case study, if accepted by the current Malt uploader.

Malt's exact upload field limits must be checked in the logged-in editor; no unverified limits are assumed.
