import json
from datetime import datetime, timezone
from pathlib import Path

from googleapiclient.discovery import build

from backend.services.ai_investigation import (
    build_site_context,
    investigate_site,
)
from backend.services.workspace_auth import (
    get_workspace_credentials,
)


ROOT_DIR = Path(__file__).resolve().parents[2]

CONFIG_FILE = (
    ROOT_DIR
    / "secrets"
    / "workspace_config.json"
)


def load_workspace_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            "Workspace configuration not found. "
            "Run setup_incident_register first."
        )

    return json.loads(
        CONFIG_FILE.read_text(
            encoding="utf-8"
        )
    )


def append_incident_to_sheet(
    site_id,
    ai_result=None,
):
    config = load_workspace_config()

    register = config[
        "incident_register"
    ]

    spreadsheet_id = register[
        "spreadsheet_id"
    ]

    spreadsheet_url = register[
        "spreadsheet_url"
    ]

    sheet_name = register[
        "sheet_name"
    ]

    context = build_site_context(
        site_id
    )

    latest = context["latest"]
    site = context["site"]

    if not ai_result:
        ai_result = investigate_site(
            site_id
        )

    credentials = (
        get_workspace_credentials()
    )

    sheets = build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )

    logged_at = (
        datetime.now(timezone.utc)
        .isoformat()
    )

    row = [[
        logged_at,
        site_id,
        site["city"],
        site["region"],
        site["technology"],
        latest["severity"],
        latest["incident_status"],
        latest["alarm_type"],
        latest["health_score"],
        latest["utilization_pct"],
        latest["latency_ms"],
        latest["packet_loss_pct"],
        latest["availability_pct"],
        ai_result.get(
            "probable_condition",
            "",
        ),
        ai_result.get(
            "confidence",
            "",
        ),
        ai_result.get(
            "executive_summary",
            "",
        ),
        ai_result.get(
            "customer_impact",
            "",
        ),
    ]]

    result = (
        sheets
        .spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=(
                f"'{sheet_name}'!A:Q"
            ),
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={
                "values": row
            },
        )
        .execute()
    )

    updates = result.get(
        "updates",
        {}
    )

    return {
        "status": "LOGGED",
        "site_id": site_id,
        "spreadsheet_url": (
            spreadsheet_url
        ),
        "updated_range": updates.get(
            "updatedRange"
        ),
        "updated_cells": updates.get(
            "updatedCells"
        ),
        "ai_mode": ai_result.get(
            "mode"
        ),
    }
