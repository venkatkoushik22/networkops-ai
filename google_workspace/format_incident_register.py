import json
from pathlib import Path

from googleapiclient.discovery import build

from backend.services.workspace_auth import (
    get_workspace_credentials,
)


ROOT = Path(__file__).resolve().parents[1]

CONFIG = (
    ROOT
    / "secrets"
    / "workspace_config.json"
)


def main():
    config = json.loads(
        CONFIG.read_text(
            encoding="utf-8"
        )
    )

    register = config[
        "incident_register"
    ]

    spreadsheet_id = register[
        "spreadsheet_id"
    ]

    credentials = (
        get_workspace_credentials()
    )

    sheets = build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )

    metadata = (
        sheets
        .spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id
        )
        .execute()
    )

    sheet_id = (
        metadata["sheets"][0]
        ["properties"]["sheetId"]
    )

    requests = [
        # Freeze header
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    },
                },
                "fields": (
                    "gridProperties."
                    "frozenRowCount"
                ),
            }
        },

        # Header styling
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 17,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.06,
                            "green": 0.09,
                            "blue": 0.13,
                        },
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": {
                                "red": 0.88,
                                "green": 0.93,
                                "blue": 0.97,
                            },
                        },
                        "verticalAlignment": (
                            "MIDDLE"
                        ),
                        "wrapStrategy": (
                            "WRAP"
                        ),
                    }
                },
                "fields": (
                    "userEnteredFormat"
                ),
            }
        },

        # Wrap all incident rows
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 17,
                },
                "cell": {
                    "userEnteredFormat": {
                        "verticalAlignment": (
                            "TOP"
                        ),
                        "wrapStrategy": (
                            "WRAP"
                        ),
                    }
                },
                "fields": (
                    "userEnteredFormat."
                    "verticalAlignment,"
                    "userEnteredFormat."
                    "wrapStrategy"
                ),
            }
        },

        # Standard columns A-M
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 13,
                },
                "properties": {
                    "pixelSize": 125
                },
                "fields": "pixelSize",
            }
        },

        # AI Condition
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 13,
                    "endIndex": 14,
                },
                "properties": {
                    "pixelSize": 260
                },
                "fields": "pixelSize",
            }
        },

        # AI Confidence
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 14,
                    "endIndex": 15,
                },
                "properties": {
                    "pixelSize": 120
                },
                "fields": "pixelSize",
            }
        },

        # AI Summary + Potential Impact
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 15,
                    "endIndex": 17,
                },
                "properties": {
                    "pixelSize": 360
                },
                "fields": "pixelSize",
            }
        },
    ]

    (
        sheets
        .spreadsheets()
        .batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": requests
            },
        )
        .execute()
    )

    print(
        "NetworkOps Incident Register formatted."
    )


if __name__ == "__main__":
    main()
