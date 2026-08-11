import base64
from email.message import EmailMessage

from googleapiclient.discovery import build

from backend.services.ai_investigation import (
    build_site_context,
    investigate_site,
)
from backend.services.workspace_auth import (
    get_workspace_credentials,
)


def send_ops_summary(
    site_id,
    recipient,
    ai_result=None,
    report_url=None,
):
    context = build_site_context(
        site_id
    )

    if not ai_result:
        ai_result = investigate_site(
            site_id
        )

    site = context["site"]
    latest = context["latest"]
    deviation = context["deviation"]
    window = context["window_24h"]

    credentials = (
        get_workspace_credentials()
    )

    gmail = build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )

    subject = (
        f"[{latest['severity']}] "
        f"NetworkOps AI Summary - {site_id}"
    )

    actions = "\n".join(
        f"{index}. {action}"
        for index, action in enumerate(
            ai_result.get(
                "recommended_actions",
                [],
            ),
            start=1,
        )
    )

    evidence = "\n".join(
        f"- {item}"
        for item in ai_result.get(
            "evidence",
            [],
        )
    )

    report_section = ""

    if report_url:
        report_section = (
            "\nINCIDENT REPORT\n"
            f"{report_url}\n"
        )

    body = f"""NETWORKOPS AI / OPERATIONS SUMMARY

Synthetic Telecom Operations Demonstration

NETWORK ELEMENT
Site: {site_id}
Location: {site["city"]} / {site["region"]}
Technology: {site["technology"]}

CURRENT STATE
Severity: {latest["severity"]}
Incident Status: {latest["incident_status"]}
Alarm: {latest["alarm_type"]}
Health Score: {latest["health_score"]:.1f}

CURRENT TELEMETRY
Utilization: {latest["utilization_pct"]:.2f}%
Latency: {latest["latency_ms"]:.2f} ms
Packet Loss: {latest["packet_loss_pct"]:.2f}%
Availability: {latest["availability_pct"]:.4f}%

BASELINE DEVIATION
Latency: {deviation["latency_pct"]:+.2f}%
Utilization: {deviation["utilization_pct"]:+.2f}%
Packet Loss: {deviation["packet_loss_pct"]:+.2f}%

24-HOUR EVENTS
Warnings: {window["warning_events"]}
Critical Events: {window["critical_events"]}

VERTEX AI ASSESSMENT
Condition: {ai_result.get("probable_condition", "")}
Confidence: {ai_result.get("confidence", "")}

{ai_result.get("executive_summary", "")}

EVIDENCE
{evidence}

RECOMMENDED ENGINEERING ACTIONS
{actions}

POTENTIAL SERVICE IMPACT
{ai_result.get("customer_impact", "")}
{report_section}
Analysis Mode: {ai_result.get("mode", "UNKNOWN")}
Model: {ai_result.get("model") or "Local Telemetry Engine"}

This message was generated from synthetic telecom telemetry
for demonstration and portfolio purposes.
"""

    message = EmailMessage()

    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(
        body
    )

    encoded_message = (
        base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()
    )

    result = (
        gmail
        .users()
        .messages()
        .send(
            userId="me",
            body={
                "raw": encoded_message
            },
        )
        .execute()
    )

    return {
        "status": "SENT",
        "site_id": site_id,
        "recipient": recipient,
        "message_id": result.get("id"),
        "thread_id": result.get(
            "threadId"
        ),
        "ai_mode": ai_result.get(
            "mode"
        ),
    }
