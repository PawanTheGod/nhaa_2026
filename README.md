# NHAA & DOSJE Portal 2026 🇮🇳

A pixel-perfect, accessible, and responsive multi-page web application replicating the **Ministry of Social Justice & Empowerment (DOSJE)** and the **National Helpline Against Atrocities (NHAA - NHAPOA)** official portals.

---

## 🏛️ Features

- **Department of Social Justice & Empowerment (DOSJE) Home**:
  - Full-width hero carousel with official Ministry campaign banners.
  - Interactive **Associated Organisations 3-Column Mega Menu** (`COMMISSIONS`, `CORPORATIONS`, `FOUNDATION / AUTONOMOUS BODIES`, `SCHEME SPECIFIC THEMATIC PORTALS`).
  - Real-time statistics banner for Cumulative Disbursements, Beneficiary Coverage, and FY Releases.
  - Explore User Personas slider (`Beneficiary` & `Government Official`).
  - Dynamic **Our Offerings** catalog (`Schemes`, `Vacancies`, `Tenders`).
  - Vivid Blue Footer with NeGD, Digital India Corporation, and official Samavesh Sahayak assistant widget.

- **NHAA / NHAPOA Portal (`/nhaa`)**:
  - Toll-Free 24x7 Helpline **14566** for PCR Act 1955 & SC/ST PoA Act 1989.
  - Interactive Action Modules: **Register Grievance**, **Register Rescue**, **Track Status**.
  - 5-Stage **Grievance Closure Process** workflow tracker.
  - SAMBAL 2021 navigation sidebar.

- **SAMAVESH Citizen Portals (`/samavesh`)**:
  - Dedicated access mechanism for SCW, SMILE Transgender, NOS, NMBA, and NHAA.

- **Comprehensive Subpages**:
  - **Schemes & Services (`/schemes`)**: Filterable scheme catalog with keyword search and application guidelines.
  - **About Us (`/about-us`)**: Vision, Mission, and Leadership portraits.
  - **Vacancies (`/vacancies`)** & **Tenders (`/tenders`)**: Recruitment circulars and procurement notices.
  - **Contact Us (`/contact-us`)**: Headquarters directory, national helplines, and public grievance form.

---

## 🚀 Tech Stack

- **React 19** + **Vite**
- **React Router DOM v7**
- **Tailwind CSS v4** + Custom UX4G Design System
- **Lucide Icons** & Vector SVGs

---

## 🏗️ Project Architecture

This project is split into three layers:

### 1. Frontend - Public Portal (React + Vite)
The citizen-facing DOSJE/NHAA portal clone (existing, already built).

### 2. Backend - Case API (FastAPI)
Located in `backend/`. The single shared PostgreSQL-backed API that every
channel (Portal, Chatbot, IVRS, Mobile App) writes to and reads from.

**Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/cases/` | Create a case (any channel) |
| `GET`  | `/api/cases/` | List cases (role-filtered) |
| `GET`  | `/api/cases/{id}` | Full case detail + risk assessments |
| `PATCH` | `/api/cases/{id}` | Update case status |
| `POST` | `/api/risk-assessments/` | AI module posts SVI score + risk tier |
| `GET`  | `/api/risk-assessments/case/{id}` | Get all risk assessments for a case |
| `GET`  | `/api/stats/cases` | Aggregate stats (for State/Ministry dashboards) |
| `GET`  | `/api/stats/trend` | Weekly trend (cases + avg SVI) |
| `GET`  | `/api/stats/districts` | District comparison table |
| `GET`  | `/api/stats/states` | State-by-state comparison |
| `GET`  | `/docs` | Swagger UI (automatic OpenAPI docs) |
| `GET`  | `/ws` | WebSocket for real-time events |

**Database tables (7):** `cases`, `victims`, `risk_assessments`, `officers`,
`notifications`, `audit_logs`, `sla_deadlines`

### 3. Admin Panel (React - Vinit's screens)
- `/admin/district` - Case queue sorted by risk tier, with SLACountdown + Escalate button
- `/admin/state` - Aggregate stats, trend charts, district comparison table
- `/admin/ministry` - National overview, state-by-state comparison, trend charts

**Reusable components:** `RiskBadge`, `SLACountdown`, `StatsCard`, `TrendChart`,
`StateComparisonTable`, `AdminLayout`

---

## 🚀 Getting Started

### Frontend
```bash
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173)

### Backend
```bash
cd backend
# Windows:
run.bat start
# Or manually:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

### Running the synchronization test
```bash
cd backend
run.bat test
# Or:
python -m pytest tests/test_sync.py -v -s
```

### Supabase integration
See [`.kilo/command/supabase-mcp.md`](.kilo/command/supabase-mcp.md) for MCP
server setup instructions. The backend connects to Supabase PostgreSQL via
the `DATABASE_URL` environment variable in `backend/.env`.

---

## 🔐 Supabase Connection

1. **Add MCP server:**
   ```bash
   claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=muzemjdlrxuewvcdwxpm&features=docs%2Caccount%2Cdatabase%2Cdebugging%2Cdevelopment%2Cfunctions%2Cbranching"
   ```

2. **Authenticate:**
   ```bash
   claude /mcp
   ```

3. **Set env vars** (`backend/.env`):
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:<password>@db.muzemjdlrxuewvcdwxpm.supabase.co:5432/postgres
   ```

4. **Run migrations** (when switching to Supabase):
   ```bash
   python -m alembic upgrade head
   ```

---

## 🧪 Tests

The synchronization test (`backend/tests/test_sync.py`) validates:

1. **4 simulated channel POSTs** (Portal, Chatbot, IVRS, Mobile App)
2. **All 4 show up** in a single `GET /cases` call
3. **All 4 trigger WebSocket push** events within 1-2 seconds
4. **Role-based filtering** blocks district officer from other districts
5. **AI risk assessment** links score to case + pushes WS event
6. **PATCH updates** trigger WS events
7. **Audit log** captures every action (append-only)
8. **End-to-end pipeline**: Portal case -> AI assessment -> status update -> audit trail

---

## 📡 Data Contract

See [`backend/docs/data_contract.md`](backend/docs/data_contract.md) for the
full field-by-field data contract shared between Vinit (backend), Pawan (frontend),
Aditya (auth), Aatmman+Vedika (AI), and Pushp (notifications).

---

## 👤 Vinit's Domain (Central Database + Backend + Admin Screens)

**Responsibilities:**
- Central Case API (FastAPI + PostgreSQL/Supabase)
- 7-table schema with Alembic migrations
- Real-time WebSocket push for live updates
- Role-based row filtering (operator, district, state, ministry)
- 3 Supervisory Admin screens: District, State, Ministry

### What was built and tested:

1. **Schema & Migrations (7 tables):**
   - `cases` — case records with channel_of_origin, status, district, state
   - `victims` — pseudonymous victim references (never store PII in plain text)
   - `risk_assessments` — SVI scores, risk tiers, flags (JSON), explanations
   - `officers` — role-based access (operator, district, state, ministry, police, etc.)
   - `notifications` — delivery tracking for response agencies
   - `audit_logs` — append-only log of all actions
   - `sla_deadlines` — legal deadline tracking per case

2. **API Endpoints:**
   - `POST /api/cases/` — create case from any channel
   - `GET /api/cases/` — list cases (filtered by role/district/state query params)
   - `GET /api/cases/{id}` — full detail including risk assessments
   - `PATCH /api/cases/{id}` — update status
   - `POST /api/risk-assessments/` — AI module posts scores
   - `GET /api/risk-assessments/case/{id}` — get assessments for a case
   - `GET /api/stats/*` — aggregate statistics for dashboards
   - `WebSocket /ws` — real-time broadcast of case/risk changes

3. **Admin Screens (accessible at `/admin/*`):**
   - `/admin/district` — Case queue sorted by risk tier, SLACountdown per row, Escalate button, WebSocket live updates
   - `/admin/state` — StatsCards (totals, tier breakdown, resolution rate), TrendChart, StateComparisonTable
   - `/admin/ministry` — National overview with StateComparisonTable and TrendCharts

4. **Reusable Components:**
   - `RiskBadge` — color-coded risk tier display
   - `SLACountdown` — deadline timer with amber→red color shift
   - `StatsCard` — labelled aggregate number
   - `TrendChart` — line/bar chart using Recharts
   - `StateComparisonTable` — sortable comparison table

### Sync Verification (Step 8 requirement):
All 7 tests in `backend/tests/test_sync.py` pass — confirmed that:
- 4 simulated channel POSTs (Portal, Chatbot, IVRS, Mobile App) all appear in `GET /cases`
- All 4 trigger WebSocket push events within 1-2 seconds
- Role-based filtering blocks district officers from other districts' cases
- AI risk assessments link to cases and trigger WS events
- PATCH updates trigger WS events
- Audit log captures all actions (append-only)
- Full end-to-end pipeline works: Portal case → AI assessment → status update → audit trail

### Supabase Migration Notes:
- Connection string requires URL-encoded `@` characters in password (`@` → `%40`)
- `alembic/env.py` must escape `%` as `%%` for configparser interpolation
- Enum types use `DO $$ ... EXCEPTION WHEN duplicate_object` blocks for idempotency
- Use `postgresql.ENUM(..., create_type=False)` in migrations when enum already exists

---

Content and design inspired by Department of Social Justice & Empowerment, Ministry of Social Justice & Empowerment, Government of India.
