# Verification record

Date: 28 September 2026 (Europe/Berlin). Environment: macOS, Python 3.14, local browser.

Thirteen behavioral tests passed: six classifier checks, five persistence/export regressions, and two request-body boundary checks. Coverage includes unknown-vocabulary abstention, category selection, score normalization, Unicode, correction provenance, independent reviews of identical text, consistent training counts, empty CSV review fields, and multibyte document payloads. Local HTTP checks verified training import, classification, human feedback, CSV export, origin rejection and unknown-route errors. A browser interaction classified a separate request as Sales and confirmed it in the review queue. The screenshot dataset is a small, explicitly labeled verification fixture; these results do not measure real-world model accuracy.

## Reproduce

Run `python3 -m unittest discover -s tests -v`. Then start the app and use the supplied fixtures as explained in the README.

## Browser checks

The visible user interface was exercised against the running backend. The captures in `screenshots/` are actual outputs, not rendered mockups.

## Unverified

Scores are not calibrated probabilities. The included dataset is for functional verification, not a trained business model. A deployment should use representative business examples and a separate held-out evaluation set. This version is a single-user local tool with no authentication, cloud hosting, email ingestion, or automatic downstream actions.
