# Notification / Dispatch Service — Pushp's module

## What was added

| File | Purpose |
|---|---|
| `app/services/notifications.py` | Core logic: tier -> recipient mapping, idempotency check, pending/confirm state machine |
| `app/routes/notifications.py` | API routes: `POST /api/risk-assessments/{id}/dispatch`, `POST /api/cases/{id}/officer-decision`, `GET /api/cases/{id}/notifications` |
| `tests/conftest.py` (extended) | Shared session-wide E2E test log (`log_result()`), used by every test file so results combine into one CSV |
| `tests/test_notifications.py` | 10 tests: all 4 tiers, idempotency, the confirmation bypass attempt, the real API endpoint |
| `tests/test_e2e_channels.py` | 17 tests: full pipeline (case -> risk assessment -> notification -> confirm) for all 4 channels x all 4 tiers, plus a check that all 4 channels land in one shared case list |
| `tests/test_log.csv` | Generated, dated, unified test log across every test file — the demo artifact |
| `docs/pushp_notification_service.md` | This file |
| `src/services/api.js` (extended) | Added `getCaseNotifications()` and `confirmOfficerDecision()` |
| `src/pages/admin/OperatorScreen.jsx` (rewired) | The "Confirm Action" button now calls the real API instead of a placeholder alert; notification log refreshes live over the websocket |

## Changes to existing files

- `app/main.py` — registered the new `notifications_router`
- `app/routes/risk_assessments.py` — after a risk assessment is created, automatically calls `process_risk_assessment()` so notifications are created without any manual trigger
- `src/services/api.js` — two new exported functions
- `src/pages/admin/OperatorScreen.jsx` — real confirm/view-case handlers replacing placeholders

No existing files were rewritten wholesale — only small, additive edits. `test_sync.py` (Vinit's original sync test) still passes unchanged (verified: 34/34 total tests pass, 17 of them new).

## A bug this testing found and fixed

While writing the channel x tier E2E tests, `test_full_pipeline_per_channel_and_tier[low-...]` failed: Low-tier notifications were staying `"pending"` forever instead of being marked `"sent"` (logged). The original code had an explicit `if risk_tier == low: pass` branch based on a "logged only, never sent" reading of the design doc — but the schema has no `logged_only` status, and leaving it `pending` incorrectly implies something is still waiting to be dispatched. Fixed: Low/Moderate/High are all marked `sent` immediately (nothing to wait for); only Critical stays `pending` until an officer confirms. This is a good concrete example of why the full E2E test matters more than testing each tier in isolation — the isolated tier tests didn't catch this because they didn't assert on `status` for Low specifically.

## Integration gap this found and fixed (frontend)

`CaseDetailPanel.jsx`'s "Confirm Action" button (built by Pawan) existed but only called `window.alert(...)` with a placeholder message — it never actually hit the backend. Wired it to `POST /api/cases/{id}/officer-decision` for real, with sending/done/error UI feedback and a live notification-log refresh over the websocket.

## How it works

1. AI module (or a test script, until Aatmman/Vedika's real model lands) POSTs to `POST /api/risk-assessments/`
2. That route automatically calls `process_risk_assessment()`, which:
   - Checks idempotency (has this `risk_assessment_id` already been processed?)
   - Looks up the tier -> recipients mapping
   - Creates `Notifications` rows
   - **Low/Moderate/High**: immediately marked `sent`
   - **Critical**: left `pending`, tagged `requires_confirmation: true`
3. An officer calls `POST /api/cases/{id}/officer-decision` — the **only** code path that can flip a Critical notification to `sent`. No bypass exists.
4. All notification state changes broadcast over the existing `/ws` websocket.

## Tier -> recipient mapping (from the SIH design doc)

| Tier | Recipients | Auto-dispatch? |
|---|---|---|
| Low | operator | Yes (logged) |
| Moderate | district | Yes |
| High | district, police, dlsa | Yes |
| Critical | district, state, police, witness_protection, medical | **No — held pending until officer confirms** |

## Running the tests

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate   # or source .venv/bin/activate on mac/linux
pip install -r requirements.txt
python -m pytest tests/ -v
```

34/34 tests pass as of this build (7 from `test_sync.py`, 10 from `test_notifications.py`, 17 from `test_e2e_channels.py`). `tests/test_log.csv` regenerates each run with a fresh timestamp.

## What is genuinely still needed — and NOT verifiable from a sandboxed dev environment

- **Aatmman/Vedika's real AI model.** It does not exist anywhere in this codebase yet. This module already works identically with real or synthetic risk-assessment data — no changes needed on this side when it lands.
- **Real Postgres/Supabase connection.** `config.py` still points at a placeholder Supabase URL with no API key; the app defaults to local SQLite. Verifying the real shared cloud database requires actual credentials and network access neither available in this build environment.
- **Aditya's JWT auth.** Still mock `localStorage` sessions in `adminAuth.js`. `confirmed_by` on the officer-decision endpoint is currently free-text — once JWT lands, it should be pulled from the authenticated officer's token instead of passed by the caller.
- **Real alert channel (SMTP/SMS/push).** Notifications are written to the DB and broadcast over websocket only; nothing is actually emailed or texted yet.
- **Live browser click-through of the Admin Panel.** The frontend build is verified clean (`npm run build` succeeds) and the API wiring is verified correct in code, but this was not visually tested in a running browser — do a manual pass through `/admin/operator` once the backend is running locally to see the real "Confirm Action" flow end-to-end.
