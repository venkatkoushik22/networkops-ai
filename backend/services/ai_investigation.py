import json
import os
from datetime import timedelta

from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions

from backend.services.network_data import load_data


PROJECT_ID = os.getenv(
    "GOOGLE_CLOUD_PROJECT",
    "networkops-ai-venkat",
)

LOCATION = os.getenv(
    "GOOGLE_CLOUD_LOCATION",
    "global",
)

MODEL_NAME = os.getenv(
    "NETWORKOPS_GEMINI_MODEL",
    "gemini-2.5-flash",
)


def pct_change(current, baseline):
    if baseline == 0:
        return 0.0

    return round(
        ((current - baseline) / baseline) * 100,
        2,
    )


def build_site_context(site_id):
    df = load_data()

    site = df[
        df["site_id"] == site_id
    ].copy()

    if site.empty:
        raise ValueError(
            f"Network site '{site_id}' was not found."
        )

    site = site.sort_values("timestamp")

    latest = site.iloc[-1]

    end_time = site["timestamp"].max()

    start_time = (
        end_time
        - timedelta(hours=24)
    )

    window = site[
        site["timestamp"] >= start_time
    ].copy()

    normal = site[
        site["severity"] == "NORMAL"
    ]

    if normal.empty:
        normal = site

    baseline_latency = float(
        normal["latency_ms"].median()
    )

    baseline_utilization = float(
        normal["utilization_pct"].median()
    )

    baseline_packet_loss = float(
        normal["packet_loss_pct"].median()
    )

    alarm_counts = (
        window[
            window["alarm_type"] != "NO_ALARM"
        ]["alarm_type"]
        .value_counts()
        .to_dict()
    )

    return {
        "site_id": site_id,

        "site": {
            "city": str(latest["city"]),
            "region": str(latest["region"]),
            "technology": str(
                latest["technology"]
            ),
            "bandwidth_mbps": int(
                latest["bandwidth_mbps"]
            ),
        },

        "latest": {
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

            "alarm_type": str(
                latest["alarm_type"]
            ),

            "severity": str(
                latest["severity"]
            ),

            "incident_status": str(
                latest["incident_status"]
            ),
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

        "deviation": {
            "latency_pct": pct_change(
                float(latest["latency_ms"]),
                baseline_latency,
            ),

            "utilization_pct": pct_change(
                float(latest["utilization_pct"]),
                baseline_utilization,
            ),

            "packet_loss_pct": pct_change(
                float(latest["packet_loss_pct"]),
                baseline_packet_loss,
            ),
        },

        "window_24h": {
            "sample_count": int(
                len(window)
            ),

            "warning_events": int(
                (
                    window["severity"]
                    == "WARNING"
                ).sum()
            ),

            "critical_events": int(
                (
                    window["severity"]
                    == "CRITICAL"
                ).sum()
            ),

            "peak_utilization_pct": round(
                float(
                    window[
                        "utilization_pct"
                    ].max()
                ),
                2,
            ),

            "peak_latency_ms": round(
                float(
                    window[
                        "latency_ms"
                    ].max()
                ),
                2,
            ),

            "peak_packet_loss_pct": round(
                float(
                    window[
                        "packet_loss_pct"
                    ].max()
                ),
                2,
            ),

            "minimum_availability_pct": round(
                float(
                    window[
                        "availability_pct"
                    ].min()
                ),
                4,
            ),

            "alarm_frequency": {
                str(key): int(value)
                for key, value
                in alarm_counts.items()
            },
        },
    }


def local_fallback(context, error_message):
    latest = context["latest"]

    evidence = []

    if latest["utilization_pct"] >= 80:
        evidence.append(
            f"Utilization is elevated at "
            f"{latest['utilization_pct']:.1f}%."
        )

    if latest["latency_ms"] >= 70:
        evidence.append(
            f"Latency is elevated at "
            f"{latest['latency_ms']:.1f} ms."
        )

    if latest["packet_loss_pct"] >= 3:
        evidence.append(
            f"Packet loss is elevated at "
            f"{latest['packet_loss_pct']:.2f}%."
        )

    if latest["availability_pct"] < 99:
        evidence.append(
            f"Availability is degraded at "
            f"{latest['availability_pct']:.3f}%."
        )

    if not evidence:
        evidence.append(
            "Current telemetry is within normal thresholds."
        )

    return {
        "site_id": context["site_id"],
        "mode": "LOCAL_FALLBACK",
        "model": None,

        "probable_condition": (
            latest["alarm_type"]
            .replace("_", " ")
            .title()
        ),

        "confidence": (
            "MEDIUM"
            if latest["severity"] != "NORMAL"
            else "LOW"
        ),

        "executive_summary": (
            "Local telemetry analysis was used because "
            "Vertex AI was unavailable."
        ),

        "evidence": evidence,

        "recommended_actions": [
            "Inspect upstream transport path health.",
            "Review recent routing and capacity changes.",
            "Compare adjacent network elements for correlated degradation.",
        ],

        "customer_impact": (
            "Potential service degradation may include "
            "higher latency, packet loss, or reduced throughput."
        ),

        "fallback_reason": error_message,
        "context": context,
    }


def investigate_site(site_id):
    context = build_site_context(
        site_id
    )

    public_demo = os.getenv(
        "NETWORKOPS_PUBLIC_DEMO",
        "0",
    ).lower() in {
        "1",
        "true",
        "yes",
    }

    if public_demo:
        return local_fallback(
            context,
            "Public demo mode",
        )

    prompt = f"""
You are NetworkOps AI, a telecom network operations
engineering assistant.

All telemetry supplied below is synthetic portfolio data.

Analyze the network element using ONLY the supplied data.

Focus on:

- current operational condition
- utilization, latency and packet-loss correlation
- deviation from baseline
- recent warning and critical events
- likely engineering cause
- engineering investigation actions
- potential customer impact; do not claim actual customer impact as fact unless customer-impact measurements are explicitly provided

Return valid JSON only.

Use exactly these fields:

{{
  "probable_condition": "short diagnosis",
  "confidence": "LOW | MEDIUM | HIGH",
  "executive_summary": "2-4 sentence technical summary",
  "evidence": [
    "evidence item"
  ],
  "recommended_actions": [
    "action item"
  ],
  "customer_impact": "short impact assessment"
}}

TELEMETRY DATA:

{json.dumps(context, indent=2)}
"""

    try:
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
            http_options=HttpOptions(
                api_version="v1"
            ),
        )

        response = (
            client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=GenerateContentConfig(
                    temperature=0.15,
                    response_mime_type=(
                        "application/json"
                    ),
                ),
            )
        )

        result = json.loads(
            response.text
        )

        required = {
            "probable_condition",
            "confidence",
            "executive_summary",
            "evidence",
            "recommended_actions",
            "customer_impact",
        }

        if not required.issubset(
            result.keys()
        ):
            raise ValueError(
                "Gemini returned incomplete JSON."
            )

        result["site_id"] = site_id
        result["mode"] = "VERTEX_AI"
        result["model"] = MODEL_NAME
        result["context"] = context

        return result

    except Exception as exc:
        return local_fallback(
            context,
            str(exc),
        )
