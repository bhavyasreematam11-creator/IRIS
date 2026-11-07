# IRIS — Intelligent Incident Response System
<p align="center">
  <img src="https://img.shields.io/badge/IRIS-v1.0.0-2563EB?style=for-the-badge&logo=shield&logoColor=white" alt="IRIS Version" />
  <img src="https://img.shields.io/badge/Theme-Blue%20%26%20White%20SaaS-173B72?style=for-the-badge" alt="Theme" />
  <img src="https://img.shields.io/badge/Memory-Hindsight%20AI-059669?style=for-the-badge" alt="Hindsight Memory" />
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <b>Turning Past Incidents into Future Intelligence.</b>
</p>

---

## 📖 Table of Contents
- [About IRIS](#-about-iris)
- [The Problem](#-the-problem)
- [Key Objectives](#-key-objectives)
- [Core Features](#-core-features)
- [Visual Design & Theme](#-visual-design--theme)
- [Architecture & Technology Stack](#-architecture--technology-stack)
- [How Hindsight Memory Works (Retain & Recall)](#-how-hindsight-memory-works-retain--recall)
- [Installation & Quickstart](#-installation--quickstart)
- [Configuration & Environment Variables](#-configuration--environment-variables)
- [Interactive Demonstration Workflow](#-interactive-demonstration-workflow)
- [Automated Testing](#-automated-testing)
- [Current Limitations](#-current-limitations)
- [Future Roadmap](#-future-roadmap)
- [License](#-license)

---

## ⚡ About IRIS

**IRIS (Intelligent Incident Response System)** is an AI-powered enterprise assistant built for Site Reliability Engineers (SREs), DevOps teams, and on-call responders. 

Unlike traditional chatbot assistants that forget everything once a session ends, IRIS implements **persistent, long-term AI agent memory using [Hindsight](https://hindsight.vectorize.io/)**. When an incident occurs, IRIS retrieves historical precedents, compares error signatures, and delivers evidence-backed troubleshooting steps. When an investigation wraps up, verified postmortem findings are stored back into Hindsight so future incidents benefit from that retained intelligence.

---

## 🛑 The Problem

Technical incidents are rarely unique:
1. **Recurring Failures:** Up to 70% of infrastructure outages repeat earlier failure patterns (e.g. database connection pool exhaustion, Redis memory saturation, TLS certificate renewal failures).
2. **Knowledge Silos & Amnesia:** Tribal knowledge lives in disparate Slack threads, Jira tickets, and postmortem Google Docs that are rarely referenced during high-stress outages.
3. **Stateless AI Chatbots:** Standard LLMs lack memory of your company's actual infrastructure topology and historical troubleshooting workflows.

---

## 🎯 Key Objectives

- **Retain Postmortem Intelligence:** Automatically capture and index confirmed root causes, terminal diagnostic commands, and permanent fixes into durable memory.
- **Multi-Strategy Recall (TEMPR):** Retrieve past incidents using semantic vector similarity, BM25 keyword error matching, and graph topology.
- **Explainable Precedents:** Clearly explain *why* a historical incident matches the current failure.
- **Honest AI Reasoning:** Strictly separate confirmed facts, historical precedents, and AI-generated hypotheses. No fabricated certainty.

---

## 🌟 Core Features

- **Authentication & Responder Profiles:** Secure user registration, PBKDF2/SHA-256 salted password hashing, authentication session management, and editable responder profiles.
- **Executive Overview Dashboard:** High-level metrics for Total Incidents, Resolved Incidents, Recurring Systems, and Retained Knowledge Memories.
- **Incident Investigation Module:** End-to-end diagnosis with 1-click recurring demo templates, AI root cause hypotheses, and prioritized operational runbook steps.
- **Incident History & Audit Log:** SQLite-backed catalog with real-time filtering across severity, category, and status.
- **AI Memory Explorer:** Deep inspection of Hindsight memory banks, real-time TEMPR search tester, and chronological retain/recall audit log.
- **Knowledge Base & Runbooks:** Curated markdown postmortems with 1-click Markdown download.
- **Operational Analytics:** Plotly dark-blue charts analyzing severity distribution, incident categories, recurring systems, and memory efficiency.
- **Configurable LLM & Memory Engine:** Seamless toggle between live Hindsight, isolated local demo store, OpenAI, Gemini, or a local deterministic SRE rule engine.

---

## 🎨 Visual Design & Theme

IRIS is engineered according to a **premium enterprise Dark Blue SaaS identity**:

| Element | Hex Code | Purpose |
|---|---|---|
| **Canvas Background** | `#0B132B` | Deep Dark Blue main application canvas |
| **Surface / Cards** | `#111C3A` | Elevated Dark Blue card surfaces and containers |
| **Card Borders** | `#1E2D54` | Structural dividers and subtle card outlines |
| **Primary Accent Blue**| `#3B82F6` | Electric Blue focal highlights and primary actions |
| **Deep Royal Blue** | `#1D4ED8` | Hover states, gradients, and secondary accents |
| **Primary Text** | `#F8FAFC` | Crisp, high-contrast white text |
| **Secondary Text** | `#94A3B8` | Muted slate text for metadata, subtitles, timestamps |
| **Success / Green** | `#10B981` | Positive status, verified postmortems, memory retained |
| **Critical / Red** | `#EF4444` | High-severity alerts and production outages |

---

## 🏗️ Architecture & Technology Stack

```text
IRIS/
├── app/
│   ├── main.py                # Main Streamlit application and layout router
│   ├── agent.py               # AI Agent (OpenAI / Gemini / Local SRE Engine)
│   ├── incident_handler.py    # Incident lifecycle coordinator
│   └── views/                 # Modular page views
│       ├── auth.py            # Login & Signup portal (Dark Blue Theme)
│       ├── profile.py         # User profile & credentials manager
│       ├── overview.py        # Dashboard with KPIs and charts
│       ├── investigate.py     # Incident submission and AI analysis
│       ├── history.py         # SQLite-backed incident catalog
│       ├── memory_explorer.py # Hindsight memory bank inspector
│       ├── knowledge_base.py  # Curated postmortems & runbooks
│       ├── analytics.py       # Plotly charts and memory metrics
│       └── settings.py        # Connection config & database management
├── memory/
│   ├── hindsight_client.py    # Official Hindsight SDK client manager
│   ├── retain.py              # Structured knowledge retention engine
│   └── recall.py              # Semantic retrieval and relevance synthesis
├── database/
│   └── db.py                  # SQLite schema, CRUD operations, and audit logger
├── utils/
│   ├── config.py              # Environment configuration & theme constants
│   └── helpers.py             # Badges, custom CSS injection, ID generation
├── tests/
│   └── test_iris.py           # Automated unit and integration test suite
├── docs/
│   └── architecture.md        # Technical architecture document
├── examples/
│   └── sample_incidents.json  # Pre-seeded realistic demo incidents
├── requirements.txt           # Python package dependencies
├── .env.example               # Environment variables template
└── README.md                  # Project documentation
```

### Core Technologies
- **Python 3.12+**
- **Streamlit** (v1.30+)
- **Hindsight Client SDK** (v1.2.0, Vectorize)
- **SQLite3** (ACID persistence)
- **Plotly Express & Graph Objects** (Interactive visualizations)
- **OpenAI / Google Gemini** (Optional LLM generative synthesis)

---

## 🧠 How Hindsight Memory Works (Retain & Recall)

IRIS integrates with the official `hindsight-client` Python SDK:

### 1. RETAIN (`memory/retain.py`)
When an investigation is verified and resolved, the incident knowledge is structured into durable, searchable sections:
```python
from memory.retain import retain_incident

result = retain_incident(
    incident_id="INC-2026-0041",
    title="PostgreSQL Connection Pool Exhaustion in User Auth Service",
    category="Database",
    severity="Critical",
    affected_system="PostgreSQL Cluster (pgpool-01)",
    description="API Gateway returned 500s due to connection timeouts.",
    error_logs="FATAL: remaining connection slots are reserved for non-replication superuser connections (SQLSTATE 53300)",
    root_cause="Node.js auth service leaked connections during token refresh retry storm.",
    steps_taken="1. Inspected pg_stat_activity. 2. Terminated idle transactions. 3. Reloaded pooler.",
    resolution="Configured PgBouncer transaction pooling (pool_size=25) and fixed dangling promise in Knex."
)
```

### 2. RECALL (`memory/recall.py`)
When a new incident is submitted, IRIS queries Hindsight using multi-strategy **TEMPR** retrieval (semantic vector search, BM25 error keyword matching, entity graph links, and occurrence timestamps):
```python
from memory.recall import recall_memories

output = recall_memories(
    query="Postgres connection acquisition timeout",
    affected_system="PostgreSQL Cluster",
    error_logs="SQLSTATE 53300"
)

for match in output.matches:
    print(f"Match: {match.title} ({int(match.similarity_score * 100)}% relevance)")
    print(f"Why Relevant: {match.relevance_explanation}")
```

### 3. Graceful Offline Handling (DEMO MODE)
If no Hindsight server is running at the configured URL:
- IRIS automatically shifts to an isolated **DEMO MODE**.
- The UI surfaces a prominent `DEMO MODE` badge.
- Memory results are labeled as `DEMO MODE MEMORY` rather than falsely claiming live Hindsight connectivity.

---

## 🚀 Installation & Quickstart

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### 1. Clone & Setup
```bash
git clone https://github.com/your-username/IRIS.git
cd IRIS
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```
*(Optionally provide your `OPENAI_API_KEY` or `HINDSIGHT_API_KEY`. If left empty, IRIS operates in local deterministic SRE mode and local memory fallback out-of-the-box!)*

### 5. Launch the Application
```bash
streamlit run app/main.py
```
Open your browser at `http://localhost:8501`.

---

## ⚙️ Configuration & Environment Variables

Key parameters in `.env`:

```ini
# Hindsight Persistent Memory Settings
HINDSIGHT_BASE_URL=http://localhost:8888
HINDSIGHT_API_KEY=
HINDSIGHT_BANK_ID=iris-incident-memory
HINDSIGHT_DEMO_MODE=false

# LLM Reasoning Engine
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1

# Application Persistence
IRIS_DATABASE_PATH=iris.db
IRIS_APP_ENV=development
```

---

## 🎬 Interactive Demonstration Workflow

IRIS includes pre-configured realistic recurring incident scenarios:

### Step 1: Inspect Seeded Historical Incident
1. Navigate to **Incident History** in the left sidebar.
2. Inspect `INC-2026-0041`: *PostgreSQL Connection Pool Exhaustion in User Auth Service*.
3. Notice that this incident has a verified root cause (`SQLSTATE 53300`) and resolution (`PgBouncer transaction pooling`), marked as **Retained in Memory**.

### Step 2: Trigger a Recurring Incident Investigation
1. Navigate to **Investigate Incident**.
2. Click the quick template: **`🔄 Scenario A: PostgreSQL Pool Exhaustion`**.
3. Notice how title, category, system, symptoms, and error logs are populated.
4. Click **Start Investigation & Recall Memory**.

### Step 3: Review Memory Precedents & AI Hypotheses
1. IRIS queries Hindsight persistent memory.
2. The UI renders the **Relevant Previous Incidents** card with:
   - Match relevance score.
   - **Why this memory is relevant**: Detailed correlation of infrastructure component and `SQLSTATE 53300` symptoms.
   - Historical root cause and verified resolution.
3. Review the prioritized **Diagnostic Steps** with exact SQL/CLI commands (`SELECT pg_terminate_backend...`).

### Step 4: Confirm Resolution & Retain
1. Scroll down to the **Retain Investigation Knowledge** box.
2. Verify the root cause and applied fix.
3. Click **Confirm Resolution & Retain into Hindsight**.
4. The postmortem is preserved in persistent memory and SQLite.

---

## 🧪 Automated Testing

IRIS includes a complete test suite covering SQLite persistence, Hindsight fallback, semantic recall, investigation lifecycle, analytics calculation, and audit logging.

Run all tests:
```bash
python tests/test_iris.py
```

Expected output:
```text
test_01_db_initialization_and_samples ... ok
test_02_hindsight_connection_fallback ... ok
test_03_memory_recall_recurring_incident ... ok
test_04_full_investigation_lifecycle ... ok
test_05_analytics_summary ... ok
test_06_audit_logging ... ok

----------------------------------------------------------------------
Ran 6 tests in 11.050s

OK
```

---

## ⚠️ Current Limitations

- **Local Daemon Dependency for Live Vector Search:** Full TEMPR live vector graph search requires a running Hindsight daemon (`vectorize-io/hindsight` container or cloud instance). Without it, IRIS transparently runs in Demo Mode.
- **Single-Tenant Database:** Built on local SQLite suitable for single-team or on-call responder laptops. Multi-tenant enterprise deployment requires migrating `database/db.py` to PostgreSQL.

---

## 🔮 Future Roadmap

- [ ] **Slack & PagerDuty Integration:** Bidirectional bot to trigger IRIS investigations directly from alert channels.
- [ ] **Automated Telemetry Fetching:** Direct read-only connectors for Datadog, Prometheus, and AWS CloudWatch to auto-populate error logs.
- [ ] **Multi-Agent Debates:** Secondary SRE challenger agent to critique diagnostic hypotheses before running production commands.
- [ ] **Automated Runbook Execution:** Interactive safe CLI execution with on-call approval gates.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
