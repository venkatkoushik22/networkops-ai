import json
from pathlib import Path

from googleapiclient.discovery import build

from backend.services.workspace_auth import (
    get_workspace_credentials,
)


ROOT_DIR = Path(__file__).resolve().parents[1]

CONFIG_FILE = (
    ROOT_DIR
    / "secrets"
    / "workspace_config.json"
)


def main():
    credentials = (
        get_workspace_credentials()
    )

    sheets = build(
        "sheets",
        "v4",
        credentials=credentials,
    )

    spreadsheet_body = {
        "properties": {
            "title": (
                "NetworkOps AI - "
                "Incident Register"
            )
        },
        "sheets": [
            {
                "properties": {
                    "title": (
                        "Incident Register"
                    ),
                    "gridProperties": {
                        "frozenRowCount": 1
                    },
                }
            }
        ],
    }

    spreadsheet = (
        sheets
        .spreadsheets()
        .create(
            body=spreadsheet_body,
            fields=(
                "spreadsheetId,"
                "spreadsheetUrl,"
                "sheets.properties"
            ),
        )
        .execute()
    )

    spreadsheet_id = (
        spreadsheet["spreadsheetId"]
    )

    spreadsheet_url = (
        spreadsheet["spreadsheetUrl"]
    )

    sheet_id = (
        spreadsheet[
            "sheets"
        ][0][
            "properties"
        ][
            "sheetId"
        ]
    )

    headers = [[
        "Logged At",
        "Site ID",
        "City",
        "Region",
        "Technology",
        "Severity",
        "Incident Status",
        "Alarm Type",
        "Health Score",
        "Utilization %",
        "Latency ms",
        "Packet Loss %",
        "Availability %",
        "AI Condition",
        "AI Confidence",
        "AI Summary",
        "Potential Impact",
    ]]

    (
        sheets
        .spreadsheets()
        .values()
        .update(
            spreadsheetId=(
                spreadsheet_id
            ),
            range=(
                "'Incident Register'!A1:Q1"
            ),
            valueInputOption="RAW",
            body={
                "values": headers
            },
        )
        .execute()
    )

    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "bold": True
                        }
                    }
                },
                "fields": (
                    "userEnteredFormat."
                    "textFormat.bold"
                ),
            }
        },
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 17,
                }
            }
        },
    ]

    (
        sheets
        .spreadsheets()
        .batchUpdate(
            spreadsheetId=(
                spreadsheet_id
            ),
            body={
                "requests": requests
            },
        )
        .execute()
    )

    config = {
        "incident_register": {
            "spreadsheet_id": (
                spreadsheet_id
            ),
            "spreadsheet_url": (
                spreadsheet_url
            ),
            "sheet_name": (
                "Incident Register"
            ),
        }
    }

    CONFIG_FILE.write_text(
        json.dumps(
            config,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "NETWORKOPS WORKSPACE SETUP COMPLETE"
    )
    print(
        "-----------------------------------"
    )
    print(
        f"Spreadsheet ID : "
        f"{spreadsheet_id}"
    )
    print(
        f"Sheet          : "
        f"Incident Register"
    )
    print(
        f"Config saved   : "
        f"{CONFIG_FILE}"
    )
    print()
    print(
        "Open this Google Sheet:"
    )
    print(
        spreadsheet_url
    )


if __name__ == "__main__":
    main()
