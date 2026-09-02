# NHAA unified project brain

Read this file first in every session. Append a changelog entry after every change or conversation that affects the code or plan. Do not re-scan the whole repo unless something here is clearly stale.

**Secrets:** never paste database passwords, API keys, or `.env` values here. Local config lives in `nhaa-unified/backend/.env` copied from `nhaa-unified/.env.example`.

---

## 1. What we are building

Officer-facing AI triage for NHAA helpline **14566** (SIH 26093, MoSJE). We are **not** rebuilding the real citizen website or the real government admin backend.

Every complaint from portal / chatbot / IVRS / mobile app must hit the **same Case API**, go through the **same AI pipeline**, then appear on role-based admin screens with notifications to the right desk.

Four USPs:

1. Silent Distress Signal (covert Critical escalation)
2. Continuity-of-care memory across channels
3. AI vs officer consistency check
4. Proactive follow-up for High/Critical (not built yet)

Working tree: `c:\Users\Aatmman C Patil\Desktop\NHAA\nhaa-unified`

Workspace briefs (do not mix into the app): `aatmman.md`, `vedika.md`, `vinit.md`, `pawan.md`, `aditya updated.md`, `pushp updated.md`, `NHAA solution to be bullt.md`, `task update.md`

Archive (do not run): `nhaa_2026-main-updated` — Pushp zip with an **older frontend**.

---

## 2. How data flows

```
Portal / Chatbot / IVRS / App
        |
        v
Vinit Case API  (backend/, port 8000)
        |
        v
Vedika Perception  (perception-service/, port 8001)
        |
        v
Aatmman Agent  (NOT BUILT — next work: backend/app/services/agent/)
        |
        v
POST /api/risk-assessments/  -->  Pushp process_risk_assessment()
        |
        +--> Admin screens (Pawan front-line + Vinit supervisory)
        +--> Notifications (Critical stays pending until officer-decision)
```

Ports:

| Service | Port | How to start |
|---|---|---|
| Frontend (Vite) | 5173 | `npm run dev` in `nhaa-unified` |
| Case API | 8000 | `uvicorn app.main:app --host 0.0.0.0 --port 8000` from `nhaa-unified/backend` |
| Perception | 8001 | `python -m uvicorn api.main:app --host 0.0.0.0 --port 8001` from `nhaa-unified/perception-service` |

Frontend hash routes (Vite base `/nhaa_2026/`): `http://localhost:5173/nhaa_2026/#/...`

---

## 3. Team status

| Person | Owns | Status in this sleeve |
|---|---|---|
| Vinit | DB + Case API + District/State/Ministry screens | In GitHub main; cloned as base |
| Pawan | NHAA org page + Login/Operator/Responder | Already on GitHub main; **kept** (do not overlay Pushp `src/`) |
| Pushp | Notification/dispatch + Critical confirm gate | Overlaid into `backend/` only |
| Vedika | STT / SER / text distress / SVI fusion | Cloned into `perception-service/` |
| Aditya | JWT auth + admin API wrappers | **Missing.** Screens use mock login (`demo123`) |
| Aatmman | Agentic decision engine | **Missing.** Next task after this merge |

Pawan demo logins (password `demo123`): `operator`, `police`, `dlsa`, `medical`, `counselor`, `witness`, `district`, `state`, `ministry`

---

## 4. Sleeve file tree (what matters)

```
nhaa-unified/
  src/
    App.jsx                          # all public + admin routes
    pages/admin/                     # Login, Operator, Responder, District, State, Ministry
    pages/organisation/NhaaOrganisationPage.jsx
    components/admin/                # RiskBadge, CaseTable, CaseDetailPanel, NotificationLog, ...
    data/                            # mockUsers, operator/responder/district/state/ministry mocks
    utils/adminAuth.js
    services/api.js                  # Case API client
  backend/
    app/main.py                      # Case API + notifications router
    app/models.py                    # 7 tables; svi_score Numeric(5,2)
    app/routes/cases.py
    app/routes/risk_assessments.py   # auto-calls process_risk_assessment
    app/routes/notifications.py      # Pushp: dispatch, officer-decision, list
    app/routes/stats.py
    app/routes/websocket.py
    app/routes/audit.py
    app/services/notifications.py    # tier mapping + Critical gate
    app/services/agent/              # CREATE THIS for Aatmman (does not exist yet)
    docs/data_contract.md
    docs/pushp_notification_service.md
    tests/test_sync.py
    tests/test_notifications.py
  perception-service/                # Vedika repo, isolated
    api/main.py
    perception/schemas/perception_schema_v1.json
    perception/schemas/perception_contract.py   # to_vinit_payload()
    tests/                           # 73 unittest tests
  brain.md                           # copy of this file
```

Admin routes in `src/App.jsx`:

- `/admin/login`, `/admin` → LoginScreen
- `/admin/operator` → OperatorScreen
- `/admin/responder` → ResponderScreen
- `/admin/district` → DistrictScreen
- `/admin/state` → StateScreen
- `/admin/ministry` → MinistryScreen
- `/organisation/national-helpline-against-atrocities` → NhaaOrganisationPage

Pushp notification endpoints:

- `POST /api/risk-assessments/{id}/dispatch`
- `POST /api/cases/{id}/officer-decision`  body `{ "confirmed_by": "..." }`
- `GET /api/cases/{id}/notifications`

Case API (Vinit):

- `POST/GET /api/cases/`, `GET/PATCH /api/cases/{id}`
- `POST /api/risk-assessments/`, `GET /api/risk-assessments/case/{id}`
- `GET /api/stats/cases|trend|districts|states`
- `GET /ws`

Perception (Vedika):

- `POST /api/v1/perception/analyze`
- analytics under `/api/v1/perception/analytics/...`

---

## 5. Locked contracts

### Vedika → Aatmman (perception output)

Source of truth: `perception-service/perception/schemas/perception_schema_v1.json`

```json
{
  "schema_version": "1.0",
  "case_id": "...",
  "svi": { "score": 68, "risk_tier": "High" },
  "flags": [
    {
      "name": "intimidation",
      "confidence": 0.85,
      "signals": ["Keyword match: ...", "long pause: 4.2s"],
      "source": ["audio", "text"]
    }
  ]
}
```

Vedika already maps SVI → Low/Moderate/High/Critical. Aatmman still owns **actions, OpenRouter explanation, Critical confirmation coordination, silent signal, officer consistency, SLA predictor**. Do not rebuild perception.

### Vedika → Vinit (`to_vinit_payload()`)

```json
{
  "case_id": 101,
  "svi_score": 79.0,
  "risk_tier": "critical",
  "flags": { "suicidal_ideation": 0.85, "intimidation": 0.75 },
  "explanation_text": "...",
  "model_version": "1.0"
}
```

Vinit `flags` is a JSON object (not the array Vedika gives Aatmman). Adapter lives in `perception_contract.py`. `svi_score` columns are `Numeric(5,2)` so `100.0` fits.

### Pushp dispatch mapping

| Tier | Recipients | Auto-send? |
|---|---|---|
| low | operator | yes |
| moderate | district | yes |
| high | district, police, dlsa | yes |
| critical | district, state, police, witness_protection, medical | **pending until** `POST /api/cases/{id}/officer-decision` |

Aatmman must **call** this gate, not duplicate dispatch. Critical dispatch without confirmation must fail.

### Pawan vs Aditya (still mock)

Data contract section 7 in `backend/docs/data_contract.md` expects Aditya:

- `POST /auth/login`
- `POST /api/decisions/confirm`
- `PATCH /api/decisions/{case_id}/actioned`

Pushp implemented confirm as `POST /api/cases/{id}/officer-decision`. When wiring UI, map Pawan’s Confirm Action button to Pushp’s endpoint until Aditya exists.

---

## 6. How this sleeve was assembled (no git merge)

Do **not** `git merge` Vedika or Pushp histories into Vinit. Overlay only.

1. Clone `https://github.com/TheVinit/nhaa_2026` → `nhaa-unified` (Vinit + Pawan).
2. Copy Pushp **new** files: `notifications.py` route + service, `test_notifications.py`, `pushp_notification_service.md`.
3. Surgical patches: register router in `main.py`; auto-dispatch in `risk_assessments.py`; `Numeric(5,2)` on `svi_score`.
4. **Never** copy Pushp `src/App.jsx` (it lacks Pawan routes).
5. Clone Vedika into `perception-service/` and run on 8001. Nested `.git` removed so it is ordinary files, not a submodule.

Git remote of `nhaa-unified` is still Vinit’s repo. Do not push unless the team asks.

---

## 7. What is NOT built yet

- Aatmman agent: risk-tier constants (may refine Vedika’s), recommended actions, OpenRouter explanation, structural Critical gate, silent distress handler, officer consistency check, SLA-breach predictor endpoint, tests
- Aditya JWT + real login
- Pushp 4-channel live E2E against real AI
- Pawan Step 12 (swap mocks for real auth)
- Continuity-of-care memory and 48–72h follow-up USP

Aatmman implementation home (when we start):

`nhaa-unified/backend/app/services/agent/` plus FastAPI routes and `backend/tests/test_agent.py`

Input shape from Aatmman brief:

```json
{
  "svi_score": 0,
  "flags": [{ "name": "str", "confidence": 0.0, "signals": ["str"] }]
}
```

---

## 8. How to run locally

Frontend:

```
cd nhaa-unified
npm install
npm run dev
```

Case API:

```
cd nhaa-unified/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Perception (heavy ML deps):

```
cd nhaa-unified/perception-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001
```

Tests:

```
cd nhaa-unified/backend && pytest tests/test_sync.py tests/test_notifications.py -v
cd nhaa-unified/perception-service && python -m unittest discover tests
```

---

## 9. Changelog (append-only)

### 2026-09-02 — Unify sleeve (this session)

- Created `nhaa-unified` from TheVinit/nhaa_2026 (Vinit Case API + Pawan admin screens already on main).
- Overlaid Pushp notification service and hooked it after `POST /api/risk-assessments/`.
- Cloned Vedika into `perception-service/`, default docs/run port 8001, removed nested `.git`.
- Bumped `svi_score` to `Numeric(5,2)` in models + Alembic + data_contract.
- Sanitized `nhaa-unified/.env.example` (removed committed credentials; use local `.env`).
- Wrote this `brain.md` at workspace root and copied into `nhaa-unified/brain.md`.
- Did **not** implement Aatmman agent yet. Next conversation: start from `aatmman.md` inside `nhaa-unified`.
