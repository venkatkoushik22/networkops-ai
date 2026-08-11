from datetime import datetime, timezone

from googleapiclient.discovery import build

from backend.services.ai_investigation import (
    build_site_context,
    investigate_site,
)
from backend.services.workspace_auth import (
    get_workspace_credentials,
)


def _text_range(full_text, target):
    start = full_text.find(target)

    if start == -1:
        return None

    # Google Docs body starts at index 1.
    return {
        "startIndex": start + 1,
        "endIndex": start + len(target) + 1,
    }


def create_incident_report(
    site_id,
    ai_result=None,
):
    context = build_site_context(
        site_id
    )

    if not ai_result:
        ai_result = investigate_site(
            site_id
        )

    latest = context["latest"]
    site = context["site"]
    deviation = context["deviation"]
    window = context["window_24h"]

    credentials = (
        get_workspace_credentials()
    )

    docs = build(
        "docs",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )

    generated_at = (
        datetime.now(timezone.utc)
        .strftime("%Y-%m-%d %H:%M UTC")
    )

    document_title = (
        f"NetworkOps AI - Incident Report - "
        f"{site_id}"
    )

    document = (
        docs
        .documents()
        .create(
            body={
                "title": document_title
            }
        )
        .execute()
    )

    document_id = document[
        "documentId"
    ]

    evidence = ai_result.get(
        "evidence",
        [],
    )

    actions = ai_result.get(
        "recommended_actions",
        [],
    )

    evidence_text = "\n".join(
        f"{index:02d}  {item}"
        for index, item in enumerate(
            evidence,
            start=1,
        )
    )

    actions_text = "\n".join(
        f"{index:02d}  {item}"
        for index, item in enumerate(
            actions,
            start=1,
        )
    )

    report_text = f"""NETWORKOPS AI / INCIDENT ENGINEERING REPORT

SYNTHETIC TELECOM OPERATIONS DEMONSTRATION
Generated {generated_at}

INCIDENT OVERVIEW

Network Element     {site_id}
Location            {site["city"]} / {site["region"]}
Technology          {site["technology"]}
Provisioned Capacity {site["bandwidth_mbps"]} Mbps
Severity            {latest["severity"]}
Incident State      {latest["incident_status"]}
Active Alarm        {latest["alarm_type"]}

CURRENT TELEMETRY

Health Score        {latest["health_score"]:.1f}
Utilization         {latest["utilization_pct"]:.2f} %
Throughput          {latest["throughput_mbps"]:.2f} Mbps
Latency             {latest["latency_ms"]:.2f} ms
Packet Loss         {latest["packet_loss_pct"]:.2f} %
Availability        {latest["availability_pct"]:.4f} %

BASELINE DEVIATION

Latency             {deviation["latency_pct"]:+.2f} %
Utilization         {deviation["utilization_pct"]:+.2f} %
Packet Loss         {deviation["packet_loss_pct"]:+.2f} %

24-HOUR EVENT PROFILE

Samples             {window["sample_count"]}
Warnings            {window["warning_events"]}
Critical Events     {window["critical_events"]}
Peak Utilization    {window["peak_utilization_pct"]:.2f} %
Peak Latency        {window["peak_latency_ms"]:.2f} ms
Peak Packet Loss    {window["peak_packet_loss_pct"]:.2f} %
Minimum Availability {window["minimum_availability_pct"]:.4f} %

VERTEX AI INCIDENT ASSESSMENT

Probable Condition
{ai_result.get("probable_condition", "")}

Confidence
{ai_result.get("confidence", "")}

Engineering Summary
{ai_result.get("executive_summary", "")}

TELEMETRY EVIDENCE

{evidence_text}

RECOMMENDED ENGINEERING ACTIONS

{actions_text}

POTENTIAL SERVICE IMPACT

{ai_result.get("customer_impact", "")}

ANALYSIS ENGINE

Mode                {ai_result.get("mode", "UNKNOWN")}
Model               {ai_result.get("model") or "Local Telemetry Engine"}

This report was generated from synthetic telecom telemetry for demonstration
and portfolio purposes. AI-generated engineering recommendations require
human validation before use in real network operations.
"""

    requests = [
        {
            "insertText": {
                "location": {
                    "index": 1
                },
                "text": report_text,
            }
        }
    ]

    title_range = _text_range(
        report_text,
        "NETWORKOPS AI / INCIDENT ENGINEERING REPORT",
    )

    if title_range:
        requests.append(
            {
                "updateTextStyle": {
                    "range": title_range,
                    "textStyle": {
                        "bold": True,
                        "fontSize": {
                            "magnitude": 18,
                            "unit": "PT",
                        },
                        "foregroundColor": {
                            "color": {
                                "rgbColor": {
                                    "red": 0.08,
                                    "green": 0.22,
                                    "blue": 0.38,
                                }
                            }
                        },
                    },
                    "fields": (
                        "bold,fontSize,"
                        "foregroundColor"
                    ),
                }
            }
        )

    section_titles = [
        "INCIDENT OVERVIEW",
        "CURRENT TELEMETRY",
        "BASELINE DEVIATION",
        "24-HOUR EVENT PROFILE",
        "VERTEX AI INCIDENT ASSESSMENT",
        "TELEMETRY EVIDENCE",
        "RECOMMENDED ENGINEERING ACTIONS",
        "POTENTIAL SERVICE IMPACT",
        "ANALYSIS ENGINE",
    ]

    for heading in section_titles:
        heading_range = _text_range(
            report_text,
            heading,
        )

        if heading_range:
            requests.append(
                {
                    "updateTextStyle": {
                        "range": heading_range,
                        "textStyle": {
                            "bold": True,
                            "fontSize": {
                                "magnitude": 11,
                                "unit": "PT",
                            },
                            "foregroundColor": {
                                "color": {
                                    "rgbColor": {
                                        "red": 0.10,
                                        "green": 0.32,
                                        "blue": 0.52,
                                    }
                                }
                            },
                        },
                        "fields": (
                            "bold,fontSize,"
                            "foregroundColor"
                        ),
                    }
                }
            )

    disclaimer_range = _text_range(
        report_text,
        "SYNTHETIC TELECOM OPERATIONS DEMONSTRATION",
    )

    if disclaimer_range:
        requests.append(
            {
                "updateTextStyle": {
                    "range": disclaimer_range,
                    "textStyle": {
                        "bold": True,
                        "fontSize": {
                            "magnitude": 8,
                            "unit": "PT",
                        },
                        "foregroundColor": {
                            "color": {
                                "rgbColor": {
                                    "red": 0.45,
                                    "green": 0.45,
                                    "blue": 0.45,
                                }
                            }
                        },
                    },
                    "fields": (
                        "bold,fontSize,"
                        "foregroundColor"
                    ),
                }
            }
        )

    (
        docs
        .documents()
        .batchUpdate(
            documentId=document_id,
            body={
                "requests": requests
            },
        )
        .execute()
    )

    document_url = (
        "https://docs.google.com/document/d/"
        f"{document_id}/edit"
    )

    return {
        "status": "CREATED",
        "site_id": site_id,
        "document_id": document_id,
        "document_url": document_url,
        "title": document_title,
        "ai_mode": ai_result.get(
            "mode"
        ),
    }
