# NetworkOps AI

AI-assisted telecom network operations platform built with FastAPI, Streamlit, Google Cloud, Vertex AI, BigQuery, and Google Workspace.

NetworkOps AI simulates a New Jersey telecom operations environment and demonstrates how network telemetry can be monitored, investigated, stored, reported, and distributed through an integrated NOC workflow.

> **Important:** This project uses synthetic telecom telemetry. It does not contain Verizon, carrier, customer, or production network data.

---

## Overview

NetworkOps AI provides a telecom-focused Network Operations Center interface for monitoring simulated LTE and 5G infrastructure across New Jersey.

The platform supports:

- Network health monitoring across 50 simulated telecom sites
- Utilization, latency, packet loss, throughput, and availability analysis
- Warning and critical incident detection
- Regional and site-level operational views
- 24-hour telemetry investigation
- BigQuery-backed analytics
- Vertex AI / Gemini incident analysis
- AI-generated engineering recommendations
- Google Sheets incident registration
- Google Docs incident engineering reports
- Gmail operations-summary delivery
- Local fallback behavior when Google Cloud services are unavailable

---

## Architecture

```mermaid
flowchart TD
    A[Synthetic NJ Telecom Telemetry] --> B[Telemetry Processing]

    B --> C[(Google BigQuery)]
    B --> D[Local CSV Fallback]

    C --> E[FastAPI Operations API]
    D --> E

    E --> F[Streamlit NOC Console]

    F --> G[Network Monitoring]
    F --> H[Incident Investigation]

    H --> I[Vertex AI / Gemini 2.5 Flash]

    I --> J[AI Incident Assessment]

    J --> K[Google Sheets]
    J --> L[Google Docs]
    J --> M[Gmail]

    K --> N[Incident Register]
    L --> O[Engineering Report]
    M --> P[Operations Summary]

## Synthetic Telecom Dataset

NetworkOps AI uses a generated telecom telemetry dataset designed to mimic operational conditions across LTE and 5G network elements in New Jersey.

Dataset characteristics:

- 50 simulated telecom sites
- 33,650 telemetry records
- 7 days of historical telemetry
- 15-minute sampling intervals
- LTE and 5G technologies
- North Jersey and Central Jersey regions
- Normal, warning, and critical operating states

Telemetry fields include:

```text
timestamp
site_id
city
region
technology
bandwidth_mbps
active_users
utilization_pct
throughput_mbps
latency_ms
packet_loss_pct
availability_pct
health_score
alarm_type
severity
incident_status
```

The generator introduces realistic operational conditions such as congestion, latency degradation, packet loss, transport issues, and reduced network health.

Supported alarm states include:

```text
NO_ALARM
HIGH_UTILIZATION
CAPACITY_CONGESTION
TRANSPORT_DEGRADATION
TRANSPORT_LINK_FAILURE
```

Severity levels:

```text
NORMAL
WARNING
CRITICAL
```

All telemetry is synthetic and created specifically for this project.

---

## Network Operations Console

The Streamlit frontend is designed as a telecom Network Operations Center rather than a generic analytics dashboard.

The interface provides:

- Network-wide health status
- Normal, warning, and critical site counts
- Average availability
- Average latency
- Packet loss
- Network utilization
- Regional filtering
- Site health grid
- Current incident monitoring
- Individual network-element selection
- 24-hour utilization traces
- 24-hour latency traces
- 24-hour packet-loss traces
- Baseline deviation analysis
- Event chronology
- AI-assisted incident investigation

Operators can select a site and investigate its current operating condition directly from the NOC interface.

---

## Vertex AI Incident Investigation

NetworkOps AI integrates with Google Vertex AI using Gemini 2.5 Flash.

When an operator selects **RUN AI INVESTIGATION**, the backend builds an operational context containing:

- Current site telemetry
- Baseline metrics
- Utilization deviation
- Latency deviation
- Packet-loss deviation
- Warning-event count
- Critical-event count
- Peak utilization
- Peak latency
- Peak packet loss
- Recent alarm patterns

Gemini returns a structured incident assessment containing:

```text
Probable Condition
Confidence
Engineering Summary
Telemetry Evidence
Recommended Engineering Actions
Potential Service Impact
```

Example investigation flow:

```text
Selected Network Element
        |
        v
24-Hour Telemetry Context
        |
        v
Baseline + Incident Analysis
        |
        v
Vertex AI / Gemini 2.5 Flash
        |
        v
Structured Engineering Assessment
```

If Vertex AI is unavailable, the backend can fall back to local telemetry-based analysis so the core application remains usable.

AI-generated recommendations are intended for demonstration and require human validation before use in real network operations.

---

## Google BigQuery Analytics

Network telemetry can also be stored and queried through Google BigQuery.

Default development configuration:

```text
Project: networkops-ai-venkat
Dataset: networkops
Table: telemetry
```

The BigQuery table contains the same operational telemetry used by the NOC console and supports queries for:

- Network-wide health summaries
- Regional network summaries
- Per-site telemetry history
- Warning-event counts
- Critical-event counts
- Utilization analysis
- Latency analysis
- Packet-loss analysis

The current synthetic dataset contains:

```text
Records: 33,650
Sites: 50
```

BigQuery access is optional. The project also maintains local CSV-based telemetry so the core demonstration does not depend entirely on a live cloud subscription.

---

## Google Workspace Automation

NetworkOps AI extends incident handling beyond the monitoring console by integrating Google Workspace directly into the operational workflow.

The goal is to reduce manual handoff work after an incident is identified.

### Google Sheets Incident Register

Operators can select a network element and choose **LOG TO GOOGLE SHEETS**.

The application appends the incident to a structured Google Sheets register containing:

```text
Logged At
Site ID
City
Region
Technology
Severity
Incident Status
Alarm Type
Health Score
Utilization %
Latency ms
Packet Loss %
Availability %
AI Condition
AI Confidence
AI Summary
Potential Impact
```

The register is automatically formatted with a frozen header row, readable column widths, and wrapped AI-generated fields.

This creates a lightweight operational record that can be reviewed, filtered, or extended for incident tracking.

---

### Google Docs Engineering Reports

Operators can select **CREATE INCIDENT REPORT** to generate a structured Google Docs engineering report.

The generated report contains:

- Incident overview
- Network element and location
- Technology and provisioned capacity
- Current telemetry
- Baseline deviation
- 24-hour event profile
- Vertex AI incident assessment
- Telemetry evidence
- Recommended engineering actions
- Potential service impact
- Analysis engine metadata

The report is created directly in the authenticated user's Google Drive.

Example flow:

```text
Selected Incident
      |
      v
Telemetry + AI Assessment
      |
      v
Google Docs API
      |
      v
Incident Engineering Report
```

The report also includes a synthetic-data disclaimer and explicitly notes that AI-generated engineering recommendations require human validation.

---

### Gmail Operations Summary

NetworkOps AI can send an operational incident summary through the Gmail API.

The **SEND OPS SUMMARY** workflow includes:

- Selected network element
- Severity
- Incident status
- Active alarm
- Current telemetry
- Baseline deviation
- Vertex AI assessment
- Telemetry evidence
- Recommended engineering actions
- Potential service impact
- Link to the generated Google Docs incident report

The Gmail message is sent through the authenticated Google Workspace account using OAuth 2.0.

Example incident workflow:

```text
RUN AI INVESTIGATION
        |
        v
Structured AI Assessment
        |
        +--> LOG TO GOOGLE SHEETS
        |
        +--> CREATE INCIDENT REPORT
        |
        +--> SEND OPS SUMMARY
```

This provides a complete operational handoff flow from detection through documentation and communication.

---

## Technology Stack

### Backend

```text
Python
FastAPI
Uvicorn
Pandas
Requests
```

### Frontend

```text
Streamlit
Plotly
HTML / CSS
```

### Google Cloud

```text
Google BigQuery
Vertex AI
Gemini 2.5 Flash
Application Default Credentials
```

### Google Workspace

```text
Google Sheets API
Google Docs API
Google Drive OAuth
Gmail API
OAuth 2.0
```

---

## Project Structure

```text
networkops-ai/
|
|-- backend/
|   |-- main.py
|   |
|   `-- services/
|       |-- network_data.py
|       |-- bigquery_service.py
|       |-- ai_investigation.py
|       |-- workspace_auth.py
|       |-- sheets_service.py
|       |-- docs_service.py
|       `-- gmail_service.py
|
|-- dashboard/
|   `-- app.py
|
|-- bigquery/
|   `-- setup_bigquery.py
|
|-- data/
|   |-- generate_network_data.py
|   `-- network_telemetry.csv
|
|-- google_workspace/
|   |-- setup_incident_register.py
|   `-- format_incident_register.py
|
|-- .env.example
|-- .gitignore
|-- requirements.txt
|-- LICENSE
`-- README.md
```

---
## Local Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd networkops-ai
```

### 2. Create a virtual environment

Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Generate synthetic telemetry

```powershell
python .\data\generate_network_data.py
```

---

## Running the Application

Start the FastAPI backend in one terminal:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Start the Streamlit NOC console in a second terminal:

```powershell
python -m streamlit run .\dashboard\app.py
```

Open:

```text
http://localhost:8501
```

---

## Google Cloud Setup

The cloud integrations are optional. The local telemetry and NOC interface can operate without them.

Authenticate with Google Cloud:

```powershell
gcloud auth login
gcloud auth application-default login
```

Set the development project:

```powershell
gcloud config set project networkops-ai-venkat
```

Cloud services used by the project include:

```text
Vertex AI API
BigQuery API
Google Sheets API
Google Docs API
Google Drive API
Gmail API
```

---

## BigQuery Setup

Create and populate the telemetry warehouse with:

```powershell
python .\bigquery\setup_bigquery.py
```

The development environment uses:

```text
Dataset: networkops
Table: telemetry
```

The backend exposes cloud-backed endpoints for network summaries, regional analytics, and site telemetry.

---

## Google Workspace OAuth

Google Workspace automation uses OAuth 2.0 Desktop credentials.

Create a Google OAuth Desktop client and save the downloaded credential file locally as:

```text
secrets/credentials_workspace.json
```

Do not commit this file.

Create the Incident Register:

```powershell
python -m google_workspace.setup_incident_register
```

Format the register:

```powershell
python -m google_workspace.format_incident_register
```

On first authorization, the application opens the Google consent flow and stores the local OAuth token inside the ignored `secrets/` directory.

---

## API Endpoints

### Local network operations

```text
GET  /health
GET  /api/network/summary
GET  /api/sites
GET  /api/sites/{site_id}
GET  /api/sites/{site_id}/telemetry
GET  /api/incidents/current
GET  /api/incidents/history
GET  /api/incidents/critical
```

### Vertex AI

```text
POST /api/ai/investigate/{site_id}
```

### BigQuery

```text
GET /api/cloud/status
GET /api/cloud/network/summary
GET /api/cloud/regions
GET /api/cloud/sites/{site_id}/telemetry
```

### Google Workspace

```text
POST /api/workspace/incidents/{site_id}
POST /api/workspace/reports/{site_id}
POST /api/workspace/email/{site_id}
```

---

## Local and Cloud Modes

NetworkOps AI is designed so the portfolio demonstration is not permanently dependent on cloud billing.

```text
Google Cloud available
        |
        +--> BigQuery analytics
        +--> Vertex AI investigation
        +--> Google Workspace automation

Google Cloud unavailable
        |
        +--> Local CSV telemetry
        +--> FastAPI
        +--> Streamlit NOC console
        +--> Local investigation fallback
```

This allows the core application to remain reproducible while still demonstrating cloud-integrated operational workflows.

---

## Security

No OAuth credentials, refresh tokens, service-account keys, or API secrets should be committed to this repository.

The following are ignored:

```text
secrets/
credentials*.json
token*.json
.env
.env.*
.streamlit/secrets.toml
```

Before pushing or deploying, verify:

```powershell
git ls-files secrets
```

The command should return nothing.

Public deployments should use platform-managed secrets rather than storing credentials in source control.

Google Workspace write operations should remain disabled in public demo environments unless credentials are securely configured.

---

## Deployment Strategy

The project is intended for:

- Local development
- GitHub source hosting
- Hugging Face Spaces demonstration deployment

The public Hugging Face version can run the synthetic telemetry, FastAPI/Streamlit interface, and local analysis path without exposing personal Google Workspace credentials.

Cloud-only features can be shown as optional integrations in the public deployment.

---

## Disclaimer

This is an independent engineering portfolio project.

All network sites, telemetry values, alarms, incidents, operational conditions, and geographic assignments in the dataset are synthetic and were generated solely for demonstration purposes.

The project does not use proprietary telecom data and is not affiliated with, endorsed by, or built on behalf of Verizon or any other telecommunications carrier.

AI-generated assessments and engineering recommendations are demonstration outputs and require human review before use in a real operational environment.

---

## License and Attribution

This project includes work derived from an MIT-licensed FastAPI/Streamlit starter scaffold.

The original MIT license and copyright notice are retained in the repository.

Substantial application logic, synthetic telecom telemetry generation, NetworkOps NOC interface, BigQuery integration, Vertex AI investigation workflow, and Google Workspace automation were developed specifically for NetworkOps AI.

