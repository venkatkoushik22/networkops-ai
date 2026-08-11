from pathlib import Path

import pandas as pd


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "network_telemetry.csv"
)


def load_data():
    """
    Load NetworkOps telemetry.

    keep_default_na=False prevents operational text values
    such as 'None' from being converted into NaN.
    """
    return pd.read_csv(
        DATA_FILE,
        parse_dates=["timestamp"],
        keep_default_na=False,
    )


def get_latest_site_records():
    df = load_data()

    latest = (
        df.sort_values("timestamp")
        .groupby("site_id")
        .tail(1)
        .copy()
    )

    return latest


def records_to_dict(df):
    """
    Convert a telemetry DataFrame into JSON-safe records.
    """

    df = df.copy()

    if "timestamp" in df.columns:
        df["timestamp"] = df["timestamp"].dt.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

    # Convert to object dtype so Python None values
    # can safely replace any remaining pandas NaN values.
    df = df.astype(object)

    df = df.where(
        pd.notnull(df),
        None,
    )

    return df.to_dict(
        orient="records"
    )