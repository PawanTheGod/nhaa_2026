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

See [`backend/docs/data_contract.md`](backend/docs/data_contract.md) for field shapes needed by each screen/endpoint.

---

## 🚀 How to Run

### 1. Install dependencies (once):
```bash
npm install
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database setup:
```bash
# Copy template and fill in Supabase credentials
cp backend/.env.example backend/.env
# Note: URL-encode @ as %40 in your Supabase password
cd backend
.venv\Scripts\activate
python -m alembic upgrade head
```

### 3. Start servers:
```bash
# Terminal 1 - Backend (port 8000)
cd backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (port 5174)
cd D:\sih2026\dosje-clone
npm run dev
```

### 4. Run tests:
```bash
cd backend
.venv\Scripts\activate
python -m pytest tests/test_sync.py -v -s
```

### Access your admin screens:
- `http://localhost:5174/nhaa_2026/#/admin/district`
- `http://localhost:5174/nhaa_2026/#/admin/state`
- `http://localhost:5174/nhaa_2026/#/admin/ministry`

### API docs:
- `http://localhost:8000/docs`

---

Content and design inspired by Department of Social Justice & Empowerment, Ministry of Social Justice & Empowerment, Government of India.
