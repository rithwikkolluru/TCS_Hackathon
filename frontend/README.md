# Intelligent Branch Service Load and Customer Experience Optimizer — Frontend Layer (Member 3)

Executive-grade, production-ready React banking analytics dashboard and real-time operational optimization portal. Built with **React 18 + Vite + Tailwind CSS + React Router + Axios + Recharts + Lucide Icons + Real-Time WebSocket**.

---

## 1. Frontend Architecture & Directory Structure

```text
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── KpiCard.jsx               # Telemetry metric cards with risk badges & gradients
│   │   │   ├── RiskBadge.jsx             # LOW, MEDIUM, HIGH, CRITICAL indicators
│   │   │   ├── StatusBadge.jsx           # PENDING, ACCEPTED, REJECTED, OPTIMAL badges
│   │   │   ├── LoadingSpinner.jsx        # Accessible loading indicators
│   │   │   ├── ErrorState.jsx            # Network & 401/403/500 error display
│   │   │   ├── EmptyState.jsx            # Zero-result fallback views
│   │   │   ├── ConfirmationModal.jsx     # Manager recommendation accept/reject modal
│   │   │   ├── BranchSelector.jsx        # RBAC branch picker dropdown
│   │   │   ├── DateSelector.jsx          # Historical and future date selection
│   │   │   └── ServiceFilter.jsx         # 14-service category filter
│   │   ├── dashboard/
│   │   │   ├── BottleneckCard.jsx        # Prediction + Reason + Action AI bottleneck cards
│   │   │   ├── RecommendationCard.jsx    # Actionable AI recommendations with action triggers
│   │   │   ├── StaffingCard.jsx          # Time-slot capacity & shortage card
│   │   │   ├── AlertPanel.jsx            # Live WebSocket alert drawer
│   │   │   ├── ServiceLoadTable.jsx      # Full 14-service load matrix table
│   │   │   ├── DigitalOpportunityCard.jsx# Self-service redirection opportunities
│   │   │   └── SurgeTriggerModal.jsx     # Interactive live surge simulation trigger
│   │   └── employee/
│   │       ├── OperationalTasksCard.jsx  # Action items tailored for branch counter staff
│   │       └── CounterStatusCard.jsx     # Token serving, handling time, & station status
│   ├── pages/
│   │   ├── Login.jsx                     # Authentication page with demo quick-logins
│   │   ├── ManagerDashboard.jsx          # 7-question executive manager control center
│   │   ├── EmployeeDashboard.jsx         # Counter staff workflow & station queues
│   │   ├── RegionalDashboard.jsx         # Network command center & geographic node map
│   │   ├── BranchOverview.jsx            # Detailed branch deep-dive view
│   │   ├── ServiceLoad.jsx               # 14-service load matrix & SLA wait times
│   │   ├── Staffing.jsx                  # Peak slot deficit forecast & allocations
│   │   ├── Bottlenecks.jsx               # ML root-cause bottleneck triage
│   │   ├── Recommendations.jsx           # AI recommendations filter & decision history
│   │   ├── Feedback.jsx                  # Zero PII customer experience & NLP sentiment
│   │   ├── Alerts.jsx                    # Real-time event log & payload inspector
│   │   ├── Profile.jsx                   # Staff profile, RBAC specs & security audit
│   │   └── NotFound.jsx                  # 404 Route
│   ├── layouts/
│   │   ├── DashboardLayout.jsx           # Main wrapper with Sidebar, Topbar, & Outlet
│   │   ├── Sidebar.jsx                   # Role-based sidebar with real-time stream status
│   │   ├── Topbar.jsx                    # Branch switcher, surge trigger, & alerts bell
│   │   └── ProtectedRoute.jsx            # Client-side RBAC guard with 401/403 handling
│   ├── services/
│   │   ├── api.js                        # Central Axios instance with JWT interceptors
│   │   ├── authService.js                # POST /api/auth/login, /me, /refresh, /logout
│   │   ├── dashboardService.js           # GET /api/dashboard/summary, /bottlenecks, /service-load
│   │   ├── predictionService.js          # POST /api/predictions/footfall, /wait-time, /staff-requirement
│   │   ├── recommendationService.js      # GET /api/recommendations, POST /generate, /accept, /reject
│   │   ├── feedbackService.js            # GET /api/feedback/summary, POST /recommendation-outcome
│   │   ├── regionalService.js            # GET /api/regional/branches, /load, /bottlenecks, /staffing
│   │   ├── branchService.js              # GET /api/branches, /branches/{code}, /staff
│   │   ├── liveService.js                # POST /api/live/simulate-surge, GET /events
│   │   └── auditService.js               # GET /api/audit/logs
│   ├── hooks/
│   │   ├── useWebSocket.js               # Auto-reconnecting WebSocket hook for /ws/alerts
│   │   ├── usePolling.js                 # Controlled 30s background data polling
│   │   └── useBranch.js                  # Global branch state & RBAC constraints
│   ├── context/
│   │   ├── AuthContext.jsx               # JWT state, login, logout, and role routing
│   │   └── AlertContext.jsx              # Real-time alert state, global toasts, & reactive triggers
│   ├── charts/
│   │   ├── TrafficChart.jsx              # Historical vs AI predicted footfall (Today/Tomorrow/7D)
│   │   ├── HourlyTrafficChart.jsx        # 8 AM - 5 PM hourly footfall & surge risk
│   │   ├── WaitTimeChart.jsx             # Service wait times vs 20m SLA threshold line
│   │   ├── FeedbackChart.jsx             # Positive / Neutral / Negative sentiment donut
│   │   ├── StaffUtilizationChart.jsx     # Available vs AI required staff
│   │   └── RiskDistributionChart.jsx     # Low / Medium / High / Critical distribution
│   ├── utils/
│   │   ├── formatters.js                 # Number, time, date, & color helpers
│   │   ├── constants.js                  # 14 categories, branches, demo logins
│   │   └── cn.js                         # Tailwind class merge utility
│   ├── styles/
│   │   └── index.css                     # Tailwind imports & custom glassmorphic classes
│   ├── App.jsx                           # Application router & role protection
│   └── main.jsx                          # React 18 DOM mount
├── public/
├── .env.example
├── .env
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

---

## 2. Installation & Quickstart

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Compile production build
npm run build
```

Development server runs by default at `http://localhost:5173`.

---

## 3. Environment Variables

Create `.env` inside `frontend/`:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## 4. Demo Login Credentials

The login page provides one-click autofill for the seeded demo accounts:

| Role | Email | Password | Branch Assigned |
|---|---|---|---|
| **Manager (Hyderabad Central)** | `manager_hyd@bank.com` | `BankDemo#2026` | `BR001` |
| **Manager (Kukatpally)** | `manager_kukatpally@bank.com` | `BankDemo#2026` | `BR002` |
| **Employee (Teller)** | `teller1_hyd@bank.com` | `BankDemo#2026` | `BR001` |
| **Regional Ops Director** | `regional@bank.com` | `BankDemo#2026` | `Network Wide` |

---

## 5. Actual Member 2 Backend Endpoints Consumed

All components consume Member 2's FastAPI endpoints directly via the centralized Axios client in `src/services/api.js`:

- **Authentication (`/api/auth`)**:
  - `POST /api/auth/login` → Authenticates credentials, issues JWT access token.
  - `GET /api/auth/me` → Fetches authenticated user profile & permissions.
  - `POST /api/auth/logout` → Terminates session and writes audit log.
- **Dashboard Telemetry (`/api/dashboard`)**:
  - `GET /api/dashboard/summary?branch_id=...` → KPIs (Total customers, queue, wait, staff, high-risk services).
  - `GET /api/dashboard/bottlenecks?branch_id=...` → Risk-evaluated bottleneck list with ML explanations.
  - `GET /api/dashboard/service-load?branch_id=...` → 14-service category breakdown (queue, wait, staff).
- **ML Predictions (`/api/predictions`)**:
  - `POST /api/predictions/footfall` → Footfall forecasts with category breakdown.
  - `POST /api/predictions/wait-time` → Service wait time & risk predictions.
  - `POST /api/predictions/staff-requirement` → Required employees vs available employees for peak slots.
- **AI Recommendations & Decision Loop (`/api/recommendations` & `/api/feedback`)**:
  - `GET /api/recommendations?branch_id=...` → Retrieves active recommendations.
  - `POST /api/recommendations/generate` → Triggers AI recommendation generation on live data.
  - `POST /api/recommendations/{id}/accept` → Approves recommendation with manager operational justification.
  - `POST /api/recommendations/{id}/reject` → Declines recommendation with managerial reasoning.
  - `GET /api/recommendations/digital-redirection` → Self-service suitability scores & channel recommendations.
  - `POST /api/feedback/recommendation-outcome` → Logs real-world impact for model retraining.
- **Customer Feedback & NLP (`/api/feedback`)**:
  - `GET /api/feedback/summary?branch_id=...` → Sentiment metrics (Positive/Neutral/Negative) & key topics (Zero PII).
- **Regional Operations (`/api/regional`)**:
  - `GET /api/regional/branches` → Network branch list.
  - `GET /api/regional/load` → Multi-branch traffic, queue, wait, and risk comparison.
  - `GET /api/regional/bottlenecks` → Aggregated critical bottlenecks across network.
  - `GET /api/regional/staffing` → Network-wide employee shortages across branches.
- **Live Event Simulation & WebSocket (`/api/live` & `/ws/alerts`)**:
  - `POST /api/live/simulate-surge` → Ingests 30-50 customer queue spike and broadcasts alert.
  - `GET /api/live/events` → Recent live branch counter transactions.
  - `GET /api/audit/logs` → Immutable security compliance records.

---

## 6. Real-Time WebSocket Implementation

- **Endpoint**: `ws://localhost:8000/ws/alerts?token=<JWT_TOKEN>`
- **Events Handled**:
  - `BOTTLENECK_ALERT`
  - `STAFFING_RECOMMENDATION`
  - `QUEUE_SPIKE`
  - `WAIT_TIME_SPIKE`
  - `STAFF_SHORTAGE`
- **Reactive Workflow**:
  1. Incoming WebSocket events trigger a global toast notification in the bottom right.
  2. The unread notification badge on the bell icon and sidebar updates instantly.
  3. The active dashboard triggers a reactive silent background refresh, updating KPI cards, service load tables, and bottleneck panels without full page reload.
  4. Auto-reconnect with exponential fallback is built into `useWebSocket.js`.

---

## 7. Demo Checklist for Presentation

1. **Manager Flow**:
   - Log in as `manager_hyd@bank.com`.
   - Open Manager Dashboard → view the 7 KPI cards answering the 7 core executive questions.
   - Inspect Traffic Forecast (Today / Tomorrow / Next 7 Days).
   - Review 14-service load table and detected bottlenecks with structured **Prediction + Reason + Recommended Action**.
   - Review Actionable AI Recommendations → click **Accept** with managerial justification → observe status update to `ACCEPTED`.
2. **Live Surge Demo Flow**:
   - Click the topbar **"Simulate Live Surge"** button (or execute `python scripts/live_event_simulator.py --surge`).
   - Trigger surge on `Withdrawal` or `Loans`.
   - Observe instant WebSocket toast notification: `CRITICAL SURGE INGESTED`.
   - Notice queue spikes to ~45 and high-risk service count increments **without page reload**.
3. **Employee Flow**:
   - Log in as `teller1_hyd@bank.com`.
   - View assigned counter station, active token serving (`Call Next Ticket`), and operational tasks board.
   - Note manager-only action buttons are restricted via RBAC.
4. **Regional Ops Flow**:
   - Log in as `regional@bank.com`.
   - View 8-branch network command center.
   - Click branch nodes on the interactive geographic map or comparative matrix to drill down into branch-specific telemetry.
