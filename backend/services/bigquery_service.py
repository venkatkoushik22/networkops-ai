import os
from datetime import date, datetime

from google.cloud import bigquery


PROJECT_ID = os.getenv(
    "GOOGLE_CLOUD_PROJECT",
    "networkops-ai-venkat",
)

DATASET_ID = os.getenv(
    "NETWORKOPS_BQ_DATASET",
    "networkops",
)

TABLE_NAME = os.getenv(
    "NETWORKOPS_BQ_TABLE",
    "telemetry",
)

TABLE_ID = (
    f"{PROJECT_ID}."
    f"{DATASET_ID}."
    f"{TABLE_NAME}"
)


def get_client():
    return bigquery.Client(
        project=PROJECT_ID
    )


def json_safe(value):
    if isinstance(
        value,
        (datetime, date),
    ):
        return value.isoformat()

    return value


def row_to_dict(row):
    return {
        key: json_safe(value)
        for key, value
        in dict(row).items()
    }


def get_warehouse_status():
    client = get_client()

    table = client.get_table(
        TABLE_ID
    )

    return {
        "source": "BIGQUERY",
        "project_id": PROJECT_ID,
        "dataset": DATASET_ID,
        "table": TABLE_NAME,
        "rows": int(
            table.num_rows
        ),
        "location": table.location,
    }


def get_cloud_network_summary():
    client = get_client()

    query = f"""
    WITH latest AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY site_id
                ORDER BY timestamp DESC
            ) AS row_num

        FROM `{TABLE_ID}`
    )

    SELECT
        COUNT(*) AS total_sites,

        COUNTIF(
            severity = 'NORMAL'
        ) AS healthy_sites,

        COUNTIF(
            severity = 'WARNING'
        ) AS warning_sites,

        COUNTIF(
            severity = 'CRITICAL'
        ) AS critical_sites,

        COUNTIF(
            alarm_type != 'NO_ALARM'
        ) AS active_alarms,

        ROUND(
            AVG(health_score),
            2
        ) AS average_health_score,

        ROUND(
            AVG(latency_ms),
            2
        ) AS average_latency_ms,

        ROUND(
            AVG(packet_loss_pct),
            2
        ) AS average_packet_loss_pct,

        ROUND(
            AVG(utilization_pct),
            2
        ) AS average_utilization_pct,

        ROUND(
            AVG(availability_pct),
            4
        ) AS average_availability_pct,

        MAX(timestamp)
            AS telemetry_timestamp

    FROM latest

    WHERE row_num = 1
    """

    rows = list(
        client.query(query).result()
    )

    result = row_to_dict(
        rows[0]
    )

    result["source"] = (
        "BIGQUERY"
    )

    return result


def get_region_summary():
    client = get_client()

    query = f"""
    WITH latest AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY site_id
                ORDER BY timestamp DESC
            ) AS row_num

        FROM `{TABLE_ID}`
    )

    SELECT
        region,

        COUNT(*) AS total_sites,

        COUNTIF(
            severity = 'NORMAL'
        ) AS normal_sites,

        COUNTIF(
            severity = 'WARNING'
        ) AS warning_sites,

        COUNTIF(
            severity = 'CRITICAL'
        ) AS critical_sites,

        ROUND(
            AVG(health_score),
            2
        ) AS health_score,

        ROUND(
            AVG(utilization_pct),
            2
        ) AS utilization_pct,

        ROUND(
            AVG(latency_ms),
            2
        ) AS latency_ms,

        ROUND(
            AVG(packet_loss_pct),
            2
        ) AS packet_loss_pct

    FROM latest

    WHERE row_num = 1

    GROUP BY region

    ORDER BY region
    """

    rows = client.query(
        query
    ).result()

    return [
        row_to_dict(row)
        for row in rows
    ]


def get_site_cloud_telemetry(
    site_id,
    hours=24,
):
    client = get_client()

    query = f"""
    WITH site_window AS (
        SELECT
            MAX(timestamp)
                AS max_timestamp

        FROM `{TABLE_ID}`

        WHERE site_id = @site_id
    )

    SELECT
        timestamp,
        site_id,
        city,
        region,
        technology,
        bandwidth_mbps,
        active_users,
        utilization_pct,
        throughput_mbps,
        latency_ms,
        packet_loss_pct,
        availability_pct,
        health_score,
        alarm_type,
        severity,
        incident_status

    FROM `{TABLE_ID}`,
         site_window

    WHERE site_id = @site_id

      AND timestamp >= DATETIME_SUB(
          max_timestamp,
          INTERVAL @hours HOUR
      )

    ORDER BY timestamp
    """

    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "site_id",
                "STRING",
                site_id,
            ),
            bigquery.ScalarQueryParameter(
                "hours",
                "INT64",
                hours,
            ),
        ]
    )

    rows = list(
        client.query(
            query,
            job_config=config,
        ).result()
    )

    return {
        "site_id": site_id,
        "source": "BIGQUERY",
        "window_hours": hours,
        "sample_count": len(rows),
        "telemetry": [
            row_to_dict(row)
            for row in rows
        ],
    }
