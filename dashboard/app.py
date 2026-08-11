import html
import os
from datetime import datetime
from textwrap import dedent

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


API_BASE = "http://127.0.0.1:8000"

PUBLIC_DEMO = os.getenv(
    "NETWORKOPS_PUBLIC_DEMO",
    "0",
).lower() in {
    "1",
    "true",
    "yes",
}


st.set_page_config(
    page_title="NetworkOps AI",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# HELPERS
# =========================================================

def render_html(markup: str):
    st.html(
        dedent(markup).strip()
    )


@st.cache_data(ttl=10)
def get_json(endpoint: str):
    response = requests.get(
        f"{API_BASE}{endpoint}",
        timeout=8,
    )
    response.raise_for_status()
    return response.json()


def make_trace(
    df,
    column,
    title,
    suffix="",
    threshold=None,
):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df[column],
            mode="lines",
            line=dict(
                width=1.6,
            ),
            hovertemplate=(
                "%{x|%H:%M}<br>"
                "%{y:.2f}"
                + suffix
                + "<extra></extra>"
            ),
        )
    )

    if threshold is not None:
        fig.add_hline(
            y=threshold,
            line_dash="dot",
            opacity=0.35,
        )

    fig.update_layout(
        height=150,
        margin=dict(
            l=8,
            r=8,
            t=28,
            b=8,
        ),
        title=dict(
            text=title,
            font=dict(size=10),
            x=0,
        ),
        paper_bgcolor="#090e14",
        plot_bgcolor="#090e14",
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(100,116,139,0.12)",
            zeroline=False,
            tickfont=dict(size=8),
            ticksuffix=suffix,
        ),
        font=dict(
            family="Consolas",
            color="#9eb0c4",
        ),
        hoverlabel=dict(
            font_family="Consolas",
        ),
    )

    return fig


# =========================================================
# CSS
# =========================================================

render_html(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 18% 4%,
                rgba(38, 82, 124, 0.12),
                transparent 24%
            ),
            #070a0f;
        color: #d8e1eb;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1650px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    * {
        font-family: Inter, "Segoe UI", sans-serif;
    }

    .noc-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        border: 1px solid #26313f;
        background: #0c1118;
        padding: 13px 16px;
    }

    .noc-brand {
        font-family: Consolas, monospace;
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 1.8px;
        color: #ecf3fa;
    }

    .noc-sub {
        font-family: Consolas, monospace;
        font-size: 9px;
        letter-spacing: 1px;
        color: #617084;
        margin-left: 10px;
    }

    .top-state {
        display: flex;
        gap: 22px;
        align-items: center;
        font-family: Consolas, monospace;
        font-size: 10px;
        color: #a7b5c5;
    }

    .status-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        margin-right: 6px;
    }

    .status-green {
        background: #31d69b;
        box-shadow: 0 0 9px rgba(49,214,155,.45);
    }

    .status-red {
        background: #ff5f6d;
        box-shadow: 0 0 9px rgba(255,95,109,.45);
    }

    .metric-strip {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        background: #090e14;
        border-left: 1px solid #26313f;
        border-right: 1px solid #26313f;
        border-bottom: 1px solid #26313f;
        margin-bottom: 12px;
    }

    .metric-cell {
        padding: 12px 15px;
        border-right: 1px solid #26313f;
    }

    .metric-cell:last-child {
        border-right: 0;
    }

    .metric-value {
        font-family: Consolas, monospace;
        font-size: 19px;
        color: #eef5fb;
    }

    .metric-label {
        font-family: Consolas, monospace;
        font-size: 8px;
        color: #637287;
        letter-spacing: 1.2px;
        margin-top: 4px;
    }

    .section-label {
        font-family: Consolas, monospace;
        font-size: 9px;
        color: #71839a;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
    }

    .ops-panel {
        border: 1px solid #26313f;
        background: #090e14;
        padding: 13px;
        min-height: 445px;
    }

    .site-field {
        display: grid;
        grid-template-columns: repeat(5, minmax(110px, 1fr));
        gap: 7px;
    }

    .site-node {
        position: relative;
        height: 62px;
        padding: 8px 9px;
        background: #0d131b;
        border: 1px solid #202b38;
    }

    .node-normal {
        border-left: 3px solid #31d69b;
    }

    .node-warning {
        border-left: 3px solid #f0b44d;
    }

    .node-critical {
        border-left: 3px solid #ff5f6d;
        background: #151015;
    }

    .site-id {
        font-family: Consolas, monospace;
        font-size: 9px;
        color: #d6e0e9;
    }

    .site-city {
        font-family: Consolas, monospace;
        font-size: 8px;
        color: #65758a;
        margin-top: 5px;
    }

    .site-score {
        position: absolute;
        right: 8px;
        bottom: 7px;
        font-family: Consolas, monospace;
        font-size: 12px;
        color: #c9d4de;
    }

    .incident-panel {
        border: 1px solid #26313f;
        background: #090e14;
        padding: 13px;
        min-height: 445px;
    }

    .incident-item {
        padding: 10px 0;
        border-top: 1px solid #202a36;
    }

    .incident-item:first-of-type {
        border-top: 0;
    }

    .incident-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .incident-site {
        font-family: Consolas, monospace;
        font-size: 9px;
        font-weight: 700;
    }

    .critical-tag,
    .warning-tag {
        font-family: Consolas, monospace;
        font-size: 7px;
        padding: 2px 5px;
    }

    .critical-tag {
        color: #ff7782;
        border: 1px solid #a94450;
    }

    .warning-tag {
        color: #f0b44d;
        border: 1px solid #816328;
    }

    .incident-type {
        font-size: 10px;
        color: #b7c3cf;
        margin-top: 6px;
    }

    .incident-meta {
        font-family: Consolas, monospace;
        font-size: 7px;
        color: #65758a;
        margin-top: 5px;
    }

    .investigation-shell {
        border: 1px solid #26313f;
        background: #090e14;
        padding: 15px;
        margin-top: 12px;
    }

    .investigation-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }

    .selected-site {
        font-family: Consolas, monospace;
        font-size: 18px;
        font-weight: 700;
        color: #edf4fa;
    }

    .selected-context {
        font-family: Consolas, monospace;
        font-size: 8px;
        color: #6d7d91;
    }

    .status-strip {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        margin-top: 13px;
        border-top: 1px solid #26313f;
        border-bottom: 1px solid #26313f;
    }

    .status-cell {
        padding: 11px;
        border-right: 1px solid #26313f;
    }

    .status-cell:last-child {
        border-right: none;
    }

    .status-value {
        font-family: Consolas, monospace;
        font-size: 15px;
        color: #edf4fa;
    }

    .status-name {
        font-family: Consolas, monospace;
        font-size: 7px;
        color: #65758a;
        margin-top: 4px;
        letter-spacing: 1px;
    }

    .baseline-box {
        border: 1px solid #26313f;
        background: #0b1118;
        padding: 12px;
        margin-top: 8px;
    }

    .baseline-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #1d2733;
        font-family: Consolas, monospace;
        font-size: 9px;
    }

    .baseline-row:last-child {
        border-bottom: none;
    }

    .event-box {
        border: 1px solid #26313f;
        background: #0b1118;
        padding: 12px;
        margin-top: 8px;
        max-height: 430px;
        overflow-y: auto;
    }

    .event-row {
        border-left: 2px solid #3b4a5d;
        padding: 7px 8px;
        margin-bottom: 7px;
        background: #0d131b;
    }

    .event-critical {
        border-left-color: #ff5f6d;
    }

    .event-warning {
        border-left-color: #f0b44d;
    }

    .event-time {
        font-family: Consolas, monospace;
        font-size: 7px;
        color: #71839a;
    }

    .event-code {
        font-family: Consolas, monospace;
        font-size: 9px;
        color: #d5dee7;
        margin-top: 3px;
    }

    .event-state {
        font-family: Consolas, monospace;
        font-size: 7px;
        color: #78899e;
        margin-top: 3px;
    }

    .engine-box {
        border-left: 2px solid #54789e;
        margin-top: 15px;
        padding-left: 14px;
    }

    .engine-title {
        font-family: Consolas, monospace;
        font-size: 9px;
        color: #91a8c1;
        letter-spacing: 1.3px;
    }

    .engine-text {
        font-size: 11px;
        line-height: 1.6;
        color: #c7d1db;
        margin-top: 7px;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label {
        font-family: Consolas, monospace !important;
        font-size: 9px !important;
        color: #71839a !important;
        letter-spacing: 1px;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background: #0a0f15 !important;
        border-color: #26313f !important;
        border-radius: 0 !important;
    }

    div.stButton > button {
        border-radius: 0;
        border: 1px solid #334154;
        background: #0e151e;
        color: #cbd6e0;
        font-family: Consolas, monospace;
        font-size: 9px;
    }

    </style>
    """
)


# =========================================================
# API DATA
# =========================================================

try:
    summary = get_json("/api/network/summary")
    sites = get_json("/api/sites")
    current_incidents = get_json(
        "/api/incidents/current"
    )

except requests.RequestException as exc:
    st.error(
        "NetworkOps API unavailable."
    )
    st.code(str(exc))
    st.stop()


# =========================================================
# HEADER
# =========================================================

current_time = datetime.now().strftime("%H:%M:%S")

if summary["critical_sites"] > 0:
    state = "DEGRADED"
    dot_class = "status-red"
else:
    state = "STABLE"
    dot_class = "status-green"


render_html(
    f"""
    <div class="noc-topbar">

        <div>
            <span class="noc-brand">
                NETWORKOPS / NJ CORE
            </span>

            <span class="noc-sub">
                TELECOM OPERATIONS INTELLIGENCE
            </span>
        </div>

        <div class="top-state">

            <span>
                <span class="status-dot {dot_class}"></span>
                NETWORK {state}
            </span>

            <span>
                {summary["healthy_sites"]}/{summary["total_sites"]}
                NORMAL
            </span>

            <span>
                {summary["warning_sites"]}
                WARNING
            </span>

            <span>
                {summary["critical_sites"]}
                CRITICAL
            </span>

            <span>
                {current_time} EDT
            </span>

        </div>

    </div>
    """
)


render_html(
    f"""
    <div class="metric-strip">

        <div class="metric-cell">
            <div class="metric-value">
                {summary["average_health_score"]:.1f}
            </div>
            <div class="metric-label">
                NETWORK HEALTH
            </div>
        </div>

        <div class="metric-cell">
            <div class="metric-value">
                {summary["average_availability_pct"]:.3f}%
            </div>
            <div class="metric-label">
                AVAILABILITY
            </div>
        </div>

        <div class="metric-cell">
            <div class="metric-value">
                {summary["average_latency_ms"]:.1f} ms
            </div>
            <div class="metric-label">
                AVG LATENCY
            </div>
        </div>

        <div class="metric-cell">
            <div class="metric-value">
                {summary["average_packet_loss_pct"]:.2f}%
            </div>
            <div class="metric-label">
                PACKET LOSS
            </div>
        </div>

        <div class="metric-cell">
            <div class="metric-value">
                {summary["average_utilization_pct"]:.1f}%
            </div>
            <div class="metric-label">
                UTILIZATION
            </div>
        </div>

    </div>
    """
)


# =========================================================
# FILTER
# =========================================================

command = st.text_input(
    "OPS FILTER",
    placeholder="critical | 5g | newark | north jersey",
)


filtered_sites = sites

if command.strip():

    value = command.lower().strip()

    filtered_sites = [
        site
        for site in sites
        if value in " ".join(
            str(v)
            for v in site.values()
        ).lower()
    ]


# =========================================================
# SITE FIELD
# =========================================================

left, right = st.columns(
    [3.2, 1.15],
    gap="small",
)


with left:

    blocks = []

    for site in filtered_sites[:50]:

        severity = str(
            site["severity"]
        ).lower()

        node_class = {
            "critical": "node-critical",
            "warning": "node-warning",
            "normal": "node-normal",
        }.get(
            severity,
            "node-normal",
        )

        blocks.append(
            f"""
            <div class="site-node {node_class}">

                <div class="site-id">
                    {html.escape(str(site["site_id"]))}
                </div>

                <div class="site-city">
                    {html.escape(str(site["city"]))}
                    ·
                    {html.escape(str(site["technology"]))}
                </div>

                <div class="site-score">
                    {float(site["health_score"]):.0f}
                </div>

            </div>
            """
        )

    render_html(
        f"""
        <div class="ops-panel">

            <div class="section-label">
                NETWORK SITE FIELD / CURRENT STATE
            </div>

            <div class="site-field">
                {''.join(blocks)}
            </div>

        </div>
        """
    )


with right:

    incident_blocks = []

    for incident in current_incidents[:8]:

        severity = str(
            incident["severity"]
        )

        tag_class = (
            "critical-tag"
            if severity == "CRITICAL"
            else "warning-tag"
        )

        incident_blocks.append(
            f"""
            <div class="incident-item">

                <div class="incident-header">

                    <span class="incident-site">
                        {html.escape(str(incident["site_id"]))}
                    </span>

                    <span class="{tag_class}">
                        {html.escape(severity)}
                    </span>

                </div>

                <div class="incident-type">
                    {html.escape(str(incident["alarm_type"]))}
                </div>

                <div class="incident-meta">
                    LAT {float(incident["latency_ms"]):.1f}ms
                    · LOSS {float(incident["packet_loss_pct"]):.1f}%
                    · UTIL {float(incident["utilization_pct"]):.0f}%
                </div>

            </div>
            """
        )

    if not incident_blocks:
        incident_blocks.append(
            """
            <div class="incident-item">
                <div class="incident-type">
                    NO ACTIVE INCIDENTS
                </div>
            </div>
            """
        )

    render_html(
        f"""
        <div class="incident-panel">

            <div class="section-label">
                CURRENT INCIDENTS / LIVE
            </div>

            {''.join(incident_blocks)}

        </div>
        """
    )


# =========================================================
# SELECT SITE
# =========================================================

site_ids = [
    site["site_id"]
    for site in sites
]


selected_site = st.selectbox(
    "INVESTIGATE NETWORK ELEMENT",
    site_ids,
)


try:
    detail = get_json(
        f"/api/sites/{selected_site}"
    )

    telemetry_response = get_json(
        f"/api/sites/{selected_site}/telemetry?hours=24"
    )

except requests.RequestException as exc:
    st.error(
        "Unable to load telemetry."
    )
    st.code(str(exc))
    st.stop()


latest = detail["latest"]
baseline = detail["baseline"]

telemetry = pd.DataFrame(
    telemetry_response["telemetry"]
)

telemetry["timestamp"] = pd.to_datetime(
    telemetry["timestamp"]
)


# =========================================================
# DEVIATIONS
# =========================================================

def pct_change(current, base):
    if base == 0:
        return 0

    return (
        (current - base)
        / base
        * 100
    )


latency_dev = pct_change(
    latest["latency_ms"],
    baseline["latency_ms"],
)

loss_dev = pct_change(
    latest["packet_loss_pct"],
    baseline["packet_loss_pct"],
)

util_dev = pct_change(
    latest["utilization_pct"],
    baseline["utilization_pct"],
)


# =========================================================
# INVESTIGATION HEADER
# =========================================================

render_html(
    f"""
    <div class="investigation-shell">

        <div class="investigation-header">

            <div>

                <div class="section-label">
                    INCIDENT INVESTIGATION / 24H TELEMETRY
                </div>

                <div class="selected-site">
                    {html.escape(selected_site)}
                </div>

            </div>

            <div class="selected-context">
                {html.escape(str(latest["city"]))}
                /
                {html.escape(str(latest["region"]))}
                /
                {html.escape(str(latest["technology"]))}
            </div>

        </div>


        <div class="status-strip">

            <div class="status-cell">
                <div class="status-value">
                    {latest["health_score"]:.1f}
                </div>
                <div class="status-name">
                    HEALTH SCORE
                </div>
            </div>

            <div class="status-cell">
                <div class="status-value">
                    {latest["utilization_pct"]:.1f}%
                </div>
                <div class="status-name">
                    UTILIZATION
                </div>
            </div>

            <div class="status-cell">
                <div class="status-value">
                    {latest["latency_ms"]:.1f} ms
                </div>
                <div class="status-name">
                    LATENCY
                </div>
            </div>

            <div class="status-cell">
                <div class="status-value">
                    {latest["packet_loss_pct"]:.2f}%
                </div>
                <div class="status-name">
                    PACKET LOSS
                </div>
            </div>

            <div class="status-cell">
                <div class="status-value">
                    {latest["availability_pct"]:.3f}%
                </div>
                <div class="status-name">
                    AVAILABILITY
                </div>
            </div>

        </div>

    </div>
    """
)


# =========================================================
# TELEMETRY TRACES
# =========================================================

trace_col, analysis_col = st.columns(
    [2.5, 1],
    gap="small",
)


with trace_col:

    st.plotly_chart(
        make_trace(
            telemetry,
            "utilization_pct",
            "UTILIZATION / 24H",
            "%",
            threshold=80,
        ),
        use_container_width=True,
        config={
            "displayModeBar": False
        },
    )

    st.plotly_chart(
        make_trace(
            telemetry,
            "latency_ms",
            "LATENCY / 24H",
            " ms",
            threshold=70,
        ),
        use_container_width=True,
        config={
            "displayModeBar": False
        },
    )

    st.plotly_chart(
        make_trace(
            telemetry,
            "packet_loss_pct",
            "PACKET LOSS / 24H",
            "%",
            threshold=3,
        ),
        use_container_width=True,
        config={
            "displayModeBar": False
        },
    )


# =========================================================
# BASELINE + EVENT CHRONOLOGY
# =========================================================

with analysis_col:

    render_html(
        f"""
        <div class="baseline-box">

            <div class="section-label">
                BASELINE DEVIATION
            </div>

            <div class="baseline-row">
                <span>LATENCY</span>
                <span>{latency_dev:+.1f}%</span>
            </div>

            <div class="baseline-row">
                <span>PACKET LOSS</span>
                <span>{loss_dev:+.1f}%</span>
            </div>

            <div class="baseline-row">
                <span>UTILIZATION</span>
                <span>{util_dev:+.1f}%</span>
            </div>

            <div class="baseline-row">
                <span>BASE LATENCY</span>
                <span>{baseline["latency_ms"]:.1f} ms</span>
            </div>

        </div>
        """
    )


    events = telemetry[
        telemetry["severity"].isin(
            ["WARNING", "CRITICAL"]
        )
    ].copy()

    events = events.tail(12)

    event_blocks = []

    for _, event in events.iterrows():

        event_class = (
            "event-critical"
            if event["severity"] == "CRITICAL"
            else "event-warning"
        )

        event_time = pd.to_datetime(
            event["timestamp"]
        ).strftime(
            "%H:%M"
        )

        event_blocks.append(
            f"""
            <div class="event-row {event_class}">

                <div class="event-time">
                    {event_time}
                    /
                    {html.escape(str(event["severity"]))}
                </div>

                <div class="event-code">
                    {html.escape(str(event["alarm_type"]))}
                </div>

                <div class="event-state">
                    {html.escape(str(event["incident_status"]))}
                </div>

            </div>
            """
        )


    if not event_blocks:
        event_blocks.append(
            """
            <div class="event-row">
                <div class="event-code">
                    NO EVENTS IN CURRENT WINDOW
                </div>
            </div>
            """
        )


    render_html(
        f"""
        <div class="event-box">

            <div class="section-label">
                EVENT CHRONOLOGY / LAST 24H
            </div>

            {''.join(event_blocks)}

        </div>
        """
    )


# =========================================================
# LOCAL INVESTIGATION ENGINE
# =========================================================

signals = []

if latest["utilization_pct"] >= 80:
    signals.append(
        "capacity utilization is elevated"
    )

if latest["latency_ms"] >= 70:
    signals.append(
        "latency exceeds the normal baseline"
    )

if latest["packet_loss_pct"] >= 3:
    signals.append(
        "transport packet loss is significant"
    )

if latest["availability_pct"] < 99:
    signals.append(
        "availability has degraded"
    )


if signals:

    observation = (
        "Telemetry correlation indicates "
        + "; ".join(signals)
        + "."
    )

    recommendation = (
        "Inspect upstream transport capacity, "
        "recent routing changes, alarm history, "
        "and adjacent network elements."
    )

else:

    observation = (
        "Current measurements are within "
        "expected operating ranges."
    )

    recommendation = (
        "Continue baseline monitoring. "
        "No immediate intervention indicated."
    )


render_html(
    f"""
    <div class="engine-box">

        <div class="engine-title">
            NETWORKOPS INVESTIGATION ENGINE
        </div>

        <div class="engine-text">

            <b>Observation</b><br>
            {html.escape(observation)}

            <br><br>

            <b>Recommended engineering check</b><br>
            {html.escape(recommendation)}

            <br><br>

            <span style="
                font-family:Consolas;
                font-size:8px;
                color:#64748b;
            ">
                ENGINE MODE / TELEMETRY RULES
                · GEMINI PENDING
            </span>

        </div>

    </div>
    """
)


# =========================================================
# OPERATIONS ACTIONS
# =========================================================

if st.session_state.get("active_site") != selected_site:

    st.session_state["active_site"] = selected_site

    st.session_state.pop(
        "ai_result",
        None,
    )

    st.session_state.pop(
        "sheet_result",
        None,
    )

    st.session_state.pop(
        "report_result",
        None,
    )


recipient_email = st.text_input(
    "OPS SUMMARY RECIPIENT",
    placeholder="Available in authenticated local deployment",
    key="ops_summary_recipient",
    disabled=PUBLIC_DEMO,
)

if PUBLIC_DEMO:
    st.caption(
        "PUBLIC DEMO / Google Workspace write actions are "
        "disabled to protect private OAuth credentials."
    )

action_1, action_2, action_3, action_4 = st.columns(4)


with action_1:

    run_ai = st.button(
        "RUN AI INVESTIGATION",
        use_container_width=True,
    )


with action_2:

    create_report = st.button(
        "CREATE INCIDENT REPORT",
        use_container_width=True,
        disabled=PUBLIC_DEMO,
    )


with action_3:

    log_to_sheets = st.button(
        "LOG TO GOOGLE SHEETS",
        use_container_width=True,
        disabled=PUBLIC_DEMO,
    )


with action_4:

    send_summary = st.button(
        "SEND OPS SUMMARY",
        use_container_width=True,
        disabled=PUBLIC_DEMO,
    )


# =========================================================
# VERTEX AI ACTION
# =========================================================

if run_ai:

    with st.spinner(
        "Vertex AI is correlating telemetry..."
    ):

        try:

            response = requests.post(
                f"{API_BASE}/api/ai/investigate/{selected_site}",
                timeout=90,
            )

            response.raise_for_status()

            st.session_state[
                "ai_result"
            ] = response.json()

        except requests.RequestException as exc:

            st.error(
                "AI investigation failed."
            )

            st.code(str(exc))


# =========================================================
# GOOGLE DOCS ACTION
# =========================================================

if create_report:

    with st.spinner(
        "Generating engineering report in Google Docs..."
    ):

        try:

            ai_payload = st.session_state.get(
                "ai_result"
            )

            response = requests.post(
                f"{API_BASE}/api/workspace/reports/{selected_site}",
                json=ai_payload,
                timeout=90,
            )

            response.raise_for_status()

            st.session_state[
                "report_result"
            ] = response.json()

        except requests.RequestException as exc:

            st.error(
                "Google Docs report generation failed."
            )

            st.code(str(exc))


# =========================================================
# GOOGLE SHEETS ACTION
# =========================================================

if log_to_sheets:

    with st.spinner(
        "Writing incident to Google Workspace..."
    ):

        try:

            response = requests.post(
                f"{API_BASE}/api/workspace/incidents/{selected_site}",
                timeout=90,
            )

            response.raise_for_status()

            st.session_state[
                "sheet_result"
            ] = response.json()

        except requests.RequestException as exc:

            st.error(
                "Google Sheets logging failed."
            )

            st.code(str(exc))


# =========================================================
# RESULT LINKS
# =========================================================

report_result = st.session_state.get(
    "report_result"
)

sheet_result = st.session_state.get(
    "sheet_result"
)


if report_result:

    if report_result.get(
        "site_id"
    ) == selected_site:

        st.success(
            "Incident engineering report created in Google Drive."
        )

        document_url = report_result.get(
            "document_url"
        )

        if document_url:

            st.link_button(
                "OPEN INCIDENT REPORT",
                document_url,
            )


if sheet_result:

    if sheet_result.get(
        "site_id"
    ) == selected_site:

        st.success(
            "Incident logged to NetworkOps AI Incident Register."
        )

        spreadsheet_url = sheet_result.get(
            "spreadsheet_url"
        )

        if spreadsheet_url:

            st.link_button(
                "OPEN INCIDENT REGISTER",
                spreadsheet_url,
            )


# =========================================================
# AI INCIDENT ASSESSMENT
# =========================================================

ai_result = st.session_state.get(
    "ai_result"
)


if ai_result:

    mode = html.escape(
        str(
            ai_result.get(
                "mode",
                "UNKNOWN",
            )
        )
    )

    model = html.escape(
        str(
            ai_result.get(
                "model",
                "LOCAL",
            )
        )
    )

    probable_condition = html.escape(
        str(
            ai_result.get(
                "probable_condition",
                "Unknown condition",
            )
        )
    )

    confidence = html.escape(
        str(
            ai_result.get(
                "confidence",
                "UNKNOWN",
            )
        )
    )

    executive_summary = html.escape(
        str(
            ai_result.get(
                "executive_summary",
                "",
            )
        )
    )

    customer_impact = html.escape(
        str(
            ai_result.get(
                "customer_impact",
                "",
            )
        )
    )


    evidence_items = []

    for item in ai_result.get(
        "evidence",
        [],
    ):

        evidence_items.append(
            f"""
            <div style="
                padding:7px 0;
                border-bottom:1px solid #1f2a36;
                font-size:11px;
                color:#c7d1db;
            ">

                <span style="
                    color:#71839a;
                    font-family:Consolas;
                    margin-right:7px;
                ">
                    +
                </span>

                {html.escape(str(item))}

            </div>
            """
        )


    action_items = []

    for index, item in enumerate(
        ai_result.get(
            "recommended_actions",
            [],
        ),
        start=1,
    ):

        action_items.append(
            f"""
            <div style="
                display:grid;
                grid-template-columns:28px 1fr;
                gap:8px;
                padding:8px 0;
                border-bottom:1px solid #1f2a36;
            ">

                <div style="
                    font-family:Consolas;
                    color:#71839a;
                    font-size:9px;
                ">
                    {index:02d}
                </div>

                <div style="
                    font-size:11px;
                    color:#c7d1db;
                ">
                    {html.escape(str(item))}
                </div>

            </div>
            """
        )


    if mode == "VERTEX_AI":

        engine_label = (
            "VERTEX AI / "
            + model.upper()
        )

    else:

        engine_label = (
            "LOCAL FALLBACK ENGINE"
        )


    render_html(
        f"""
        <div style="
            margin-top:14px;
            border:1px solid #304052;
            background:#091019;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:11px 14px;
                border-bottom:1px solid #26313f;
            ">

                <div style="
                    font-family:Consolas;
                    font-size:9px;
                    letter-spacing:1.5px;
                    color:#91a8c1;
                ">
                    AI INCIDENT ASSESSMENT
                </div>

                <div style="
                    font-family:Consolas;
                    font-size:8px;
                    color:#71839a;
                ">
                    {engine_label}
                </div>

            </div>


            <div style="
                display:grid;
                grid-template-columns:1.1fr .35fr;
                border-bottom:1px solid #26313f;
            ">

                <div style="
                    padding:15px;
                    border-right:1px solid #26313f;
                ">

                    <div style="
                        font-family:Consolas;
                        font-size:8px;
                        color:#71839a;
                        letter-spacing:1px;
                    ">
                        PROBABLE CONDITION
                    </div>

                    <div style="
                        font-family:Consolas;
                        font-size:17px;
                        color:#edf4fa;
                        margin-top:6px;
                    ">
                        {probable_condition}
                    </div>

                </div>


                <div style="
                    padding:15px;
                ">

                    <div style="
                        font-family:Consolas;
                        font-size:8px;
                        color:#71839a;
                        letter-spacing:1px;
                    ">
                        CONFIDENCE
                    </div>

                    <div style="
                        font-family:Consolas;
                        font-size:17px;
                        color:#edf4fa;
                        margin-top:6px;
                    ">
                        {confidence}
                    </div>

                </div>

            </div>


            <div style="
                padding:15px;
                border-bottom:1px solid #26313f;
            ">

                <div style="
                    font-family:Consolas;
                    font-size:8px;
                    color:#71839a;
                    letter-spacing:1px;
                ">
                    ENGINEERING SUMMARY
                </div>

                <div style="
                    margin-top:7px;
                    font-size:11px;
                    line-height:1.7;
                    color:#c7d1db;
                ">
                    {executive_summary}
                </div>

            </div>


            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
            ">

                <div style="
                    padding:15px;
                    border-right:1px solid #26313f;
                ">

                    <div style="
                        font-family:Consolas;
                        font-size:8px;
                        color:#71839a;
                        letter-spacing:1px;
                        margin-bottom:5px;
                    ">
                        TELEMETRY EVIDENCE
                    </div>

                    {''.join(evidence_items)}

                </div>


                <div style="
                    padding:15px;
                ">

                    <div style="
                        font-family:Consolas;
                        font-size:8px;
                        color:#71839a;
                        letter-spacing:1px;
                        margin-bottom:5px;
                    ">
                        ENGINEERING ACTIONS
                    </div>

                    {''.join(action_items)}

                </div>

            </div>


            <div style="
                padding:13px 15px;
                border-top:1px solid #26313f;
                background:#0b1118;
            ">

                <span style="
                    font-family:Consolas;
                    font-size:8px;
                    color:#71839a;
                    letter-spacing:1px;
                ">
                    POTENTIAL SERVICE IMPACT
                </span>

                <span style="
                    margin-left:12px;
                    font-size:10px;
                    color:#b9c5d1;
                ">
                    {customer_impact}
                </span>

            </div>

        </div>
        """
    )


# =========================================================
# GMAIL OPS SUMMARY
# =========================================================

if send_summary:

    recipient = (
        st.session_state
        .get(
            "ops_summary_recipient",
            "",
        )
        .strip()
    )

    if not recipient:

        st.warning(
            "Enter an operations-summary recipient first."
        )

    elif "@" not in recipient:

        st.warning(
            "Enter a valid recipient email address."
        )

    else:

        with st.spinner(
            "Sending NetworkOps operations summary..."
        ):

            try:

                current_ai = (
                    st.session_state.get(
                        "ai_result"
                    )
                )

                current_report = (
                    st.session_state.get(
                        "report_result"
                    )
                )

                report_url = None

                if current_report:
                    report_url = (
                        current_report.get(
                            "document_url"
                        )
                    )

                payload = {
                    "ai_result": current_ai,
                    "report_url": report_url,
                }

                response = requests.post(
                    f"{API_BASE}/api/workspace/email/{selected_site}",
                    params={
                        "recipient": recipient
                    },
                    json=payload,
                    timeout=120,
                )

                if response.status_code != 200:

                    st.error(
                        f"Gmail API returned HTTP "
                        f"{response.status_code}."
                    )

                    st.code(
                        response.text
                    )

                else:

                    result = response.json()

                    st.session_state[
                        "email_result"
                    ] = result

                    st.success(
                        f"Operations summary sent to "
                        f"{result.get('recipient', recipient)}."
                    )

                    message_id = result.get(
                        "message_id",
                        "UNKNOWN",
                    )

                    st.caption(
                        f"Gmail message ID: {message_id}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Could not reach the NetworkOps Gmail endpoint."
                )

                st.code(
                    str(exc)
                )


email_result = st.session_state.get(
    "email_result"
)


if email_result:

    if (
        email_result.get("site_id")
        == selected_site
    ):

        render_html(
            f"""
            <div style="
                margin-top:8px;
                border:1px solid #26313f;
                background:#0b1118;
                padding:10px 12px;
                font-family:Consolas;
                font-size:8px;
                color:#71839a;
            ">
                GMAIL DELIVERY
                &nbsp;&nbsp;/&nbsp;&nbsp;
                STATUS SENT
                &nbsp;&nbsp;/&nbsp;&nbsp;
                RECIPIENT
                {html.escape(
                    str(
                        email_result.get(
                            "recipient",
                            "",
                        )
                    )
                )}
                &nbsp;&nbsp;/&nbsp;&nbsp;
                MESSAGE
                {html.escape(
                    str(
                        email_result.get(
                            "message_id",
                            "",
                        )
                    )
                )}
            </div>
            """
        )
