# Intelligent Branch Service Load and Customer Experience Optimizer

Production-grade Data Engineering, Machine Learning, FastAPI Backend, Database, Security, and Real-Time Infrastructure for Indian Banking Branch Networks.

---

## 🏗️ Architecture & Team Roles

```
┌────────────────────────────────────────────────────────┐
│               MEMBER 1: ML & DATA FOUNDATION           │
│  - 90-Day Synthetic Indian Banking Data (Zero PII)     │
│  - Footfall & Wait Time Models (Scikit-Learn Pipelines)│
│  - Bottleneck Detector & Staff Optimization Engine     │
│  - NLP Feedback Sentiment & Digital Redirection Engine │
└───────────────────────────┬────────────────────────────┘
                            │ (In-Process ML Adapters)
┌───────────────────────────▼────────────────────────────┐
│         MEMBER 2: BACKEND, DATABASE, SECURITY & RT      │
│  - FastAPI Security Gate & PII Sanitizer               │
│  - PostgreSQL / SQLite Relational Database Engine      │
│  - JWT Bearer Authentication & Strict RBAC             │
│  - Redis Streams & WebSocket Alert Broadcast Gateway   │
│  - Continuous Learning Recommendation Feedback Loop    │
└───────────────────────────┬────────────────────────────┘
                            │ (REST APIs & WebSockets)
┌───────────────────────────▼────────────────────────────┐
│      MEMBERS 3 & 4: WEBSOCKET GATEWAY & REACT UI       │
│  - Real-time Alerting & Push Notifications             │
│  - Branch Manager, Employee & Regional Ops Dashboards  │
└────────────────────────────────────────────────────────┘
```

---

## 🏛️ Strictly Enforced Service Categories (14 Categories)
1. Loans - Payment and Sanctioning
2. Insurance
3. Deposit
4. Withdrawal
5. Account Opening
6. Credit Card
7. Debit Card
8. Locker Issuing
9. Cheque Withdrawal
10. KYC Related
11. Money Transfer
12. Aadhaar Linking
13. PAN Linking
14. Other

---

## 🏙️ Regional Banking Network Branches (Telangana & Andhra Pradesh)
- `BR001`: Hyderabad Central (Metro - Multiplier: 1.4x)
- `BR002`: Hyderabad Kukatpally (Metro - Multiplier: 1.6x)
- `BR003`: Hyderabad Secunderabad (Metro - Multiplier: 1.3x)
- `BR004`: Warangal Main (Tier-2 - Multiplier: 1.0x)
- `BR005`: Vijayawada Main (Tier-2 - Multiplier: 1.2x)
- `BR006`: Karimnagar Main (Tier-3 - Multiplier: 0.8x)
- `BR007`: Visakhapatnam Central (Tier-2 - Multiplier: 1.25x)
- `BR008`: Tirupati Main (Tier-2 - Multiplier: 1.1x)

---

## 👥 Demo Users & Role-Based Access Control (RBAC)

Password for all demo accounts: `BankDemo#2026`

| Email | Role | Branch Assignment | Description |
| :--- | :--- | :--- | :--- |
| `regional@bank.com` | `regional_ops` | `All` | Regional Operations Director: Network-wide dashboards, multi-branch comparisons, systemic bottlenecks, and regional staffing. |
| `manager_hyd@bank.com` | `manager` | `BR001` (Hyderabad Central) | Branch Manager: Branch KPIs, footfall predictions, staff requirements, bottleneck alerts, accept/reject recommendations. |
| `manager_kukatpally@bank.com` | `manager` | `BR002` (Kukatpally) | Branch Manager: Strict branch isolation to Kukatpally. |
| `teller1_hyd@bank.com` | `employee` | `BR001` (Hyderabad Central) | Branch Employee: View live queue, counter workload, bottleneck alerts. |

---

## ⚡ Quick Start & Commands

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Database
Seeds 8 branches, demo staff accounts with bcrypt password hashes, sample roster, sanitized visits, recommendations, and audit logs:
```bash
python scripts/seed_database.py
```

### 3. Start Backend Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

### 4. Run End-to-End Demonstration Scenario
Runs the complete 18-step verification scenario specified in Section 49:
```bash
python scripts/demo_scenario.py
```

### 5. Run Automated Tests
```bash
pytest backend/tests/ tests/
```

---

## 🐳 Docker Deployment

Run the complete backend stack (PostgreSQL + Redis + FastAPI Backend) in Docker:
```bash
docker compose up --build
```

---

## 📁 Repository Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/             # REST Routers (auth, branches, predictions, dashboard, etc.)
│   │   ├── core/            # Security (bcrypt, JWT), permissions (RBAC), sanitizer (PII removal)
│   │   ├── db/              # SQLAlchemy models, database connection, Pydantic schemas
│   │   ├── services/        # ML adapter, live service, audit service, Ollama/Gemini privacy pipeline
│   │   ├── websocket/       # WebSocket connection manager & alert dispatcher
│   │   ├── config.py        # Environment settings
│   │   └── main.py          # FastAPI application entrypoint
│   └── tests/               # Backend unit, RBAC, and security integration tests
├── frontend/                # Member 3 & 4 React + Vite + Tailwind + Recharts UI
│   ├── src/
│   │   ├── components/      # Glassmorphic UI components, modals, alerts
│   │   ├── pages/           # Manager, Employee, Regional, and Analytics dashboards
│   │   ├── context/         # Auth, Live WebSocket, and Notification contexts
│   │   └── services/        # API client and WebSocket clients
│   └── package.json
├── dataset/                 # Dedicated Presentation Datasets (CSV & Documentation)
├── src/
│   ├── data/                # Member 1 Synthetic generator & ETL
│   ├── features/            # Feature engineering matrices
│   ├── models/              # Footfall, wait time, bottleneck detector, live predictor
│   ├── nlp/                 # Customer feedback sentiment & topic extractor
│   ├── recommendation/      # Staff requirement, feedback loop, digital redirection
│   └── utils/               # Config & explainability engine
├── scripts/
│   ├── seed_database.py     # Database seeder
│   ├── demo_scenario.py     # End-to-end verification demonstration script
│   ├── live_event_simulator.py # Live event stream & surge generator
│   └── explore_dataset.py   # CLI presentation dataset explorer
├── docs/
│   ├── API_CONTRACT.md      # Complete REST API specifications
│   ├── INTEGRATION_STATUS.md# System validation status
│   ├── RBAC_TEST_MATRIX.md  # Security & authorization validation matrix
│   ├── ML_INTEGRATION.md    # Member 1 ML Integration Guide
│   └── BACKEND_INTEGRATION.md # Member 2 Backend & Real-time Integration Guide
├── models/                  # Trained ML model pipelines (.pkl)
├── reports/                 # JSON evaluation metrics & CSV analytics
├── .github/workflows/       # GitHub Actions CI validation workflows
├── docker-compose.yml       # PostgreSQL, Redis, and Backend orchestration
├── Dockerfile               # Multi-stage container Dockerfile
├── requirements.txt         # All ML & Backend dependencies
└── README.md
```

---

## 🔒 Security Gate & Zero-PII Compliance

- **No Raw Customer PII Stored or Returned**: Customer names, phone numbers, Aadhaar numbers, PAN numbers, full street addresses, and bank account numbers are stripped by `core/sanitizer.py` before any response leaves the backend.
- **Branch Data Isolation**: Managers and employees assigned to branch `BR001` are blocked by RBAC permission gates from viewing private operational data of other branches (HTTP 403 Forbidden).
- **Audit Logging**: Every sensitive action (`login`, `prediction_request`, `recommendation_accepted`, `surge_triggered`) is recorded in tamper-evident database audit logs.
