# NHAA Central Case API - Data Contract

This document defines the exact field names, shapes, and types for every data
flow between the **Case API** (Vinit) and the **Admin Panel** screens
(District, State, Ministry). All field names are agreed with Pawan and
Aditya so shared concepts (`case_id`, `risk_tier`) are identical across
both halves of the panel.

---

## 1. Case (POST /cases, GET /cases, PATCH /cases/{id})

### POST /cases - input JSON

```json
{
  "channel_of_origin": "portal",     // enum: portal | chatbot | ivrs | mobile_app
  "district": "Central Delhi",        // string | null
  "state": "Delhi",                   // string | null
  "incident_description": "...",     // string | null (free text)
  "incident_date": "2026-08-31T09:15:00", // ISO 8601 | null
  "language": "en",                  // default: "en"
  "is_silent_signal": false,         // boolean - covert escalation flag
  "victim_id": 1,                    // bigint FK | null
  "assigned_officer_id": 5           // bigint FK | null
}
```

### GET /cases - output JSON (array of CaseOut)

```json
[
  {
    "id": 1,
    "channel_of_origin": "portal",
    "created_at": "2026-08-31T09:15:00+00:00",
    "updated_at": "2026-08-31T09:15:00+00:00",
    "status": "new",            // enum: new | in_progress | escalated | resolved | closed
    "district": "Central Delhi",
    "state": "Delhi",
    "incident_description": "...",
    "language": "en",
    "is_silent_signal": false,
    "victim_id": null,
    "assigned_officer_id": null,
    "svi_score": 87.5,          // numeric(5,2) | null
    "risk_tier": "critical",    // enum: low | moderate | high | critical | null
    "recommended_action": "police_intervention", // string | null (always included by AI)
    "current_level": 1,         // int: 0=operator, 1=district, 2=state, 3=ministry
    "risk_assessments": []       // array of RiskAssessmentMini (empty for list view)
  }
]
```

### Query parameters for filtering

| Parameter | Type   | Description |
|-----------|--------|-------------|
| `role`    | string | `operator`, `district`, `state`, `ministry` (default: `ministry`) |
| `district`| string | Filter by district (used when role=district or operator) |
| `state`   | string | Filter by state (used when role=state) |
| `status`  | enum   | Filter by case status |
| `risk_tier`| enum  | Filter by risk tier |
| `limit`   | int    | Max results (default 100, max 500) |
| `offset`  | int    | Pagination offset (default 0) |

### Role-based row filtering

- **operator** - sees cases in their district (filtered by `district` param)
- **district** - sees all cases in their district
- **state** - sees all cases in their state (filtered by `state` param)
- **ministry** - sees everything

---

## 2. Risk Assessment (POST /risk-assessments, GET /risk-assessments/case/{id})

### POST /risk-assessments - input JSON

```json
{
  "case_id": 1,
  "svi_score": 87.5,
  "risk_tier": "critical",
  "flags": {
    "trauma": { "present": true, "confidence": 0.82, "signals": ["long pause: 4.2s"] },
    "fear": { "present": true, "confidence": 0.88, "signals": ["voice tremor"] },
    "suicidal_ideation": { "present": false, "confidence": 0.05, "signals": [] },
    "intimidation": { "present": true, "confidence": 0.84, "signals": ["threat language"] },
    "isolation": { "present": false, "confidence": 0.12, "signals": [] }
  },
  "explanation_text": "High pitch variability detected; multiple trauma markers present...",
  "model_version": "nhs-emotion-v2.1"
}
```

**Flags shape (final — per Aatmman):**
Each flag is a nested object with:
- `present` (bool) — whether this flag was detected
- `confidence` (float 0-1) — model confidence
- `signals` (list of strings) — specific signals that triggered this flag

NOT a flat boolean. The Case API stores the full nested object in `risk_assessments.flags` as JSON.

### Output JSON (RiskAssessmentOut)

```json
{
  "id": 1,
  "case_id": 1,
  "svi_score": 87.5,
  "risk_tier": "critical",
  "flags": { "trauma": true, ... },
  "explanation_text": "...",
  "created_at": "2026-08-31T09:20:00+00:00",
  "model_version": "nhs-emotion-v2.1"
}
```

---

## 3. WebSocket /ws - Real-time Events

Every insert/update to `cases` or `risk_assessments` broadcasts a JSON event:

```json
{
  "event": "case_created",        // or: case_updated, risk_assessment_created
  "data": { ... },                 // the serialized row
  "timestamp": "2026-08-31T09:15:00.000Z"
}
```

---

## 4. Admin Panel Data Contracts

### District Screen (/admin/district)

**Source:** `GET /api/cases?role=district&district={district}`

Each row expects:
- `id` (int) - case identifier
- `risk_tier` (enum) - low / moderate / high / critical
- `svi_score` (float) - 0-100
- `slaDueDate` (string, ISO) - computed deadline (not yet in API; frontend computes)
- `district` (string)
- `channel` (enum) - portal / chatbot / ivrs / mobile_app
- `created_at` (string, ISO)
- `incident_description` (string)
- `is_silent_signal` (boolean)

**Components:** RiskBadge, SLACountdown, case table with Escalate button

### State Screen (/admin/state)

**Sources:**
- `GET /api/stats/cases?role=state&state={state}` - aggregate stats
- `GET /api/stats/trend?role=state&state={state}&weeks=4` - weekly trend
- `GET /api/stats/districts?role=state&state={state}` - district comparison

Stats expects:
- `total_cases` (int)
- `tier_breakdown` - { low, moderate, high, critical }
- `resolution_rate` (float, percentage)

Trend expects array of:
- `week` (string, e.g. "2026-W35")
- `cases` (int)
- `sviAvg` (float)
- `critical` (int)

District table expects:
- `district` (string)
- `cases` (int)
- `resolved` (int)
- `resolutionRate` (float)
- `highRisk` (int)

**Components:** StatsCard, TrendChart, StateComparisonTable

### Ministry Screen (/admin/ministry)

**Sources:**
- `GET /api/stats/cases?role=ministry` - national stats
- `GET /api/stats/trend?role=ministry&weeks=4` - national trend
- `GET /api/stats/states` - state-by-state comparison

State table expects:
- `state` (string)
- `cases` (int)
- `resolved` (int)
- `resolutionRate` (float)
- `highRisk` (int)
- `critical` (int)

**Components:** StatsCard, TrendChart, StateComparisonTable

---

## 5. Shared Field Names (across Vinit + Pawan screens)

| Concept | Field name | Type |
|---------|-----------|------|
| Case identifier | `id` / `case_id` | int |
| Risk tier | `risk_tier` | enum string |
| SVI score | `svi_score` | float (0-100) |
| District | `district` | string |
| State | `state` | string |
| Channel of origin | `channel_of_origin` | enum string |
| Case status | `status` | enum string |
| Created timestamp | `created_at` | ISO datetime |
| SLA due date | `due_date` / `slaDueDate` | ISO datetime |

---

## 6. Audit Log (append-only)

| Column | Type | Notes |
|--------|------|-------|
| `id` | bigint PK | auto-increment |
| `actor` | varchar(100) | User ID or "ai_module" or "system" |
| `action` | varchar(100) | `case_created`, `status_updated`, `case_updated`, `risk_assessed` |
| `case_id` | bigint FK | nullable |
| `timestamp` | timestamp | server default now() |
| `details` | JSON | arbitrary JSON of what changed |

**This table MUST NOT be updated or deleted from.** Every officer action
and AI score is recorded here for compliance and the AI-vs-officer
consistency check (USP 3).

---

## 7. Pawan Admin Screens (Login, Operator, Responder)

### Login (`POST /auth/login` — Aditya, Step 12)

**Request:**
```json
{ "username": "operator", "password": "..." }
```

**Response:**
```json
{
  "token": "jwt...",
  "role": "operator",
  "name": "Priya Sharma",
  "district": "Central Delhi",
  "state": "Delhi"
}
```

**Redirect map:** `operator` → `/admin/operator`; `police|dlsa|medical|counselor|witness_protection` → `/admin/responder`; `district|state|ministry` → Vinit routes.

### Operator Screen — CaseTable row

Uses same `CaseOut` fields as Section 1, plus for detail panel:
- `explanation_text` (string)
- `recommended_action` (string)
- `flags` (JSON object — **nested** `{ present, confidence, signals[] }`, not flat booleans)
- `status` + `current_level` (display together; e.g. `status=escalated` + `current_level=district` — there is no separate “pending district approval” status)
- `notifications[]`: `{ recipient_role, channel, sent_at, status }`

### Operator — Allowed actions (Aatmman engine)

- `GET /api/cases/{id}/allowed-actions` → `{ "allowed_actions": ["escalate_to_district", "dispatch_police", ...] }`
- `POST /api/cases/{id}/action` body `{ "action": "escalate_to_district", "notes": "..." }`
- UI must render/submit the **exact** action strings (never a generic `"escalate"`).

### Operator — Critical confirm (`POST /api/cases/{id}/officer-decision` — Pushp)

```json
{ "case_id": 1001, "action": "confirm_critical_dispatch", "officer_id": "..." }
```

### Responder Screen — ResponderTaskCard

Uses the shared `role` enum (same field as officers / JWT), not a separate `responder_type`:

```json
{
  "case_id": 1001,
  "role": "police",
  "svi_score": 94.5,
  "risk_tier": "critical",
  "recommended_action": "police_intervention",
  "channel_of_origin": "ivrs",
  "created_at": "ISO8601",
  "district": "Central Delhi",
  "incident_description": "...",
  "actioned": false
}
```

**Filter:** `role` must match JWT `role` (one of: `police`, `dlsa`, `medical`, `counselor`, `witness_protection`).

### Responder — Mark actioned (`PATCH /api/decisions/{case_id}/actioned` — Aditya)

```json
{ "role": "police", "actioned": true }
```

### Flags shape (Aatmman / Vedika — CaseDetailPanel)

```json
{
  "trauma": { "present": true, "confidence": 0.82, "signals": ["long pause: 4.2s"] },
  "fear": { "present": true, "confidence": 0.88, "signals": ["voice tremor"] },
  "suicidal_ideation": { "present": false, "confidence": 0.05, "signals": [] },
  "intimidation": { "present": true, "confidence": 0.84, "signals": ["threat language"] },
  "isolation": { "present": false, "confidence": 0.12, "signals": [] }
}
```

### Login redirects (all 9 roles)

| role | route |
|------|-------|
| `operator` | `/admin/operator` |
| `police`, `dlsa`, `medical`, `counselor`, `witness_protection` | `/admin/responder` |
| `district` | `/admin/district` |
| `state` | `/admin/state` |
| `ministry` | `/admin/ministry` |

### WebSocket events (Operator live table)

`ws://localhost:8000/ws` — payload `{ "event", "data", "timestamp" }`

| event | Operator behaviour |
|-------|--------------------|
| `case_created` | Prepend new row |
| `case_updated` | Update matching row risk badge / fields |
| `risk_assessment_created` | Update matching row risk badge / fields |

Mock data files: `src/data/operatorMockCases.js`, `src/data/responderMockCases.js`, `src/data/mockUsers.js`.