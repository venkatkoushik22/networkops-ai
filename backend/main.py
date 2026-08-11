from datetime import timedelta

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.services.network_data import (
    get_latest_site_records,
    load_data,
    records_to_dict,
)


app = FastAPI(
    title="NetworkOps AI API",
    description="Telecom network operations, telemetry, and incident intelligence API",
    version="1.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "NetworkOps AI",
        "status": "running",
        "version": "1.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "networkops-api",
    }


@app.get("/api/network/summary")
def network_summary():
    latest = get_latest_site_records()

    normal_sites = int(
        (latest["severity"] == "NORMAL").sum()
    )

    warning_sites = int(
        (latest["severity"] == "WARNING").sum()
    )

    critical_sites = int(
        (latest["severity"] == "CRITICAL").sum()
    )

    active_alarms = int(
        (latest["alarm_type"] != "NO_ALARM").sum()
    )

    return {
        "total_sites": int(len(latest)),
        "healthy_sites": normal_sites,
        "warning_sites": warning_sites,
        "critical_sites": critical_sites,
        "active_alarms": active_alarms,

        "average_health_score": round(
            float(latest["health_score"].mean()),
            2,
        ),

        "average_latency_ms": round(
            float(latest["latency_ms"].mean()),
            2,
        ),

        "average_packet_loss_pct": round(
            float(latest["packet_loss_pct"].mean()),
            2,
        ),

        "average_utilization_pct": round(
            float(latest["utilization_pct"].mean()),
            2,
        ),

        "average_availability_pct": round(
            float(latest["availability_pct"].mean()),
            4,
        ),
    }


@app.get("/api/sites")
def get_sites():
    latest = get_latest_site_records()

    severity_order = {
        "CRITICAL": 0,
        "WARNING": 1,
        "NORMAL": 2,
    }

    latest = latest.copy()

    latest["severity_rank"] = (
        latest["severity"]
        .map(severity_order)
        .fillna(3)
    )

    latest = latest.sort_values(
        [
            "severity_rank",
            "health_score",
        ],
        ascending=[
            True,
            True,
        ],
    )

    latest = latest.drop(
        columns=["severity_rank"]
    )

    return records_to_dict(latest)


@app.get("/api/sites/{site_id}")
def get_site(site_id: str):
    df = load_data()

    site = df[
        df["site_id"] == site_id
    ].copy()

    if site.empty:
        raise HTTPException(
            status_code=404,
            detail="Network site not found",
        )

    site = site.sort_values("timestamp")

    latest = site.iloc[-1]

    recent = site.tail(96)

    normal_history = site[
        site["severity"] == "NORMAL"
    ]

    if normal_history.empty:
        baseline_latency = float(
            site["latency_ms"].median()
        )

        baseline_utilization = float(
            site["utilization_pct"].median()
        )

        baseline_packet_loss = float(
            site["packet_loss_pct"].median()
        )

    else:
        baseline_latency = float(
            normal_history[
                "latency_ms"
            ].median()
        )

        baseline_utilization = float(
            normal_history[
                "utilization_pct"
            ].median()
        )

        baseline_packet_loss = float(
            normal_history[
                "packet_loss_pct"
            ].median()
        )

    return {
        "site_id": site_id,

        "latest": {
            "timestamp": latest[
                "timestamp"
            ].strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),

            "city": latest["city"],
            "region": latest["region"],
            "technology": latest["technology"],

            "health_score": float(
                latest["health_score"]
            ),

            "utilization_pct": float(
                latest["utilization_pct"]
            ),

            "throughput_mbps": float(
                latest["throughput_mbps"]
            ),

            "latency_ms": float(
                latest["latency_ms"]
            ),

            "packet_loss_pct": float(
                latest["packet_loss_pct"]
            ),

            "availability_pct": float(
                latest["availability_pct"]
            ),

            "severity": latest["severity"],

            "alarm_type": latest[
                "alarm_type"
            ],

            "incident_status": latest[
                "incident_status"
            ],
        },

        "baseline": {
            "latency_ms": round(
                baseline_latency,
                2,
            ),

            "utilization_pct": round(
                baseline_utilization,
                2,
            ),

            "packet_loss_pct": round(
                baseline_packet_loss,
                2,
            ),
        },

        "recent_metrics": records_to_dict(
            recent
        ),
    }


@app.get("/api/sites/{site_id}/telemetry")
def get_site_telemetry(
    site_id: str,
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
    ),
):
    df = load_data()

    site = df[
        df["site_id"] == site_id
    ].copy()

    if site.empty:
        raise HTTPException(
            status_code=404,
            detail="Network site not found",
        )

    site = site.sort_values("timestamp")

    latest_timestamp = site[
        "timestamp"
    ].max()

    start_timestamp = (
        latest_timestamp
        - timedelta(hours=hours)
    )

    window = site[
        site["timestamp"]
        >= start_timestamp
    ].copy()

    return {
        "site_id": site_id,
        "window_hours": hours,
        "sample_count": int(
            len(window)
        ),
        "telemetry": records_to_dict(
            window
        ),
    }


@app.get("/api/incidents/current")
def get_current_incidents():
    latest = get_latest_site_records()

    incidents = latest[
        latest["severity"].isin(
            ["WARNING", "CRITICAL"]
        )
    ].copy()

    severity_order = {
        "CRITICAL": 0,
        "WARNING": 1,
    }

    incidents["severity_rank"] = (
        incidents["severity"]
        .map(severity_order)
        .fillna(2)
    )

    incidents = incidents.sort_values(
        [
            "severity_rank",
            "health_score",
        ],
        ascending=[
            True,
            True,
        ],
    )

    incidents = incidents.drop(
        columns=["severity_rank"]
    )

    return records_to_dict(incidents)


@app.get("/api/incidents/history")
def get_incident_history(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):
    df = load_data()

    incidents = df[
        df["severity"].isin(
            ["WARNING", "CRITICAL"]
        )
    ].copy()

    incidents = incidents.sort_values(
        "timestamp",
        ascending=False,
    )

    return records_to_dict(
        incidents.head(limit)
    )


@app.get("/api/incidents/critical")
def get_critical_incidents():
    df = load_data()

    incidents = df[
        df["severity"] == "CRITICAL"
    ].copy()

    incidents = incidents.sort_values(
        "timestamp",
        ascending=False,
    )

    return records_to_dict(
        incidents.head(100)
    )


@app.post("/api/ai/investigate/{site_id}")
def run_ai_investigation(site_id: str):
    from backend.services.ai_investigation import investigate_site

    try:
        return investigate_site(site_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@app.get("/api/cloud/status")
def cloud_status():
    from backend.services.bigquery_service import (
        get_warehouse_status,
    )

    try:
        return get_warehouse_status()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"BigQuery unavailable: {exc}",
        )


@app.get("/api/cloud/network/summary")
def cloud_network_summary():
    from backend.services.bigquery_service import (
        get_cloud_network_summary,
    )

    try:
        return get_cloud_network_summary()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"BigQuery unavailable: {exc}",
        )


@app.get("/api/cloud/regions")
def cloud_regions():
    from backend.services.bigquery_service import (
        get_region_summary,
    )

    try:
        return get_region_summary()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"BigQuery unavailable: {exc}",
        )


@app.get("/api/cloud/sites/{site_id}/telemetry")
def cloud_site_telemetry(
    site_id: str,
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
    ),
):
    from backend.services.bigquery_service import (
        get_site_cloud_telemetry,
    )

    try:
        result = get_site_cloud_telemetry(
            site_id,
            hours,
        )

        if result["sample_count"] == 0:
            raise HTTPException(
                status_code=404,
                detail="Network site not found in BigQuery",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"BigQuery unavailable: {exc}",
        )


@app.post("/api/workspace/incidents/{site_id}")
def log_workspace_incident(site_id: str):
    from backend.services.sheets_service import (
        append_incident_to_sheet,
    )

    try:
        return append_incident_to_sheet(
            site_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Google Sheets logging failed: "
                f"{exc}"
            ),
        )


@app.post("/api/workspace/reports/{site_id}")
def create_workspace_report(
    site_id: str,
    ai_result: dict | None = None,
):
    from backend.services.docs_service import (
        create_incident_report,
    )

    try:
        return create_incident_report(
            site_id,
            ai_result=ai_result,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Google Docs report generation failed: "
                f"{exc}"
            ),
        )


@app.post("/api/workspace/email/{site_id}")
def send_workspace_email(
    site_id: str,
    recipient: str,
    payload: dict | None = None,
):
    from backend.services.gmail_service import (
        send_ops_summary,
    )

    if not recipient or "@" not in recipient:
        raise HTTPException(
            status_code=400,
            detail="A valid recipient email is required.",
        )

    payload = payload or {}

    try:
        return send_ops_summary(
            site_id=site_id,
            recipient=recipient,
            ai_result=payload.get(
                "ai_result"
            ),
            report_url=payload.get(
                "report_url"
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Gmail summary delivery failed: "
                f"{exc}"
            ),
        )
