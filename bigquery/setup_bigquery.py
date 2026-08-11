from pathlib import Path

from google.cloud import bigquery


PROJECT_ID = "networkops-ai-venkat"
DATASET_NAME = "networkops"
TABLE_NAME = "telemetry"

CSV_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "network_telemetry.csv"
)


client = bigquery.Client(
    project=PROJECT_ID
)


# ---------------------------------------------------------
# DATASET
# ---------------------------------------------------------

dataset_id = (
    f"{PROJECT_ID}.{DATASET_NAME}"
)

dataset = bigquery.Dataset(
    dataset_id
)

dataset.location = "US"

dataset = client.create_dataset(
    dataset,
    exists_ok=True,
)

print(
    f"Dataset ready: {dataset_id}"
)


# ---------------------------------------------------------
# TELEMETRY TABLE SCHEMA
# ---------------------------------------------------------

table_id = (
    f"{PROJECT_ID}."
    f"{DATASET_NAME}."
    f"{TABLE_NAME}"
)


schema = [
    bigquery.SchemaField(
        "timestamp",
        "DATETIME",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "site_id",
        "STRING",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "city",
        "STRING",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "region",
        "STRING",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "technology",
        "STRING",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "bandwidth_mbps",
        "INTEGER",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "active_users",
        "INTEGER",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "utilization_pct",
        "FLOAT",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "throughput_mbps",
        "FLOAT",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "latency_ms",
        "FLOAT",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "packet_loss_pct",
        "FLOAT",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "availability_pct",
        "FLOAT",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "health_score",
        "FLOAT",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "alarm_type",
        "STRING",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "severity",
        "STRING",
        mode="REQUIRED",
    ),

    bigquery.SchemaField(
        "incident_status",
        "STRING",
        mode="REQUIRED",
    ),
]


table = bigquery.Table(
    table_id,
    schema=schema,
)

table.clustering_fields = [
    "site_id",
    "region",
    "severity",
]

table = client.create_table(
    table,
    exists_ok=True,
)

print(
    f"Table ready: {table_id}"
)


# ---------------------------------------------------------
# LOAD CSV
# ---------------------------------------------------------

job_config = (
    bigquery.LoadJobConfig(
        schema=schema,
        source_format=(
            bigquery.SourceFormat.CSV
        ),
        skip_leading_rows=1,
        write_disposition=(
            bigquery.WriteDisposition.WRITE_TRUNCATE
        ),
    )
)


with open(
    CSV_FILE,
    "rb",
) as source_file:

    load_job = (
        client.load_table_from_file(
            source_file,
            table_id,
            job_config=job_config,
        )
    )


print(
    "Uploading NetworkOps telemetry..."
)

load_job.result()


table = client.get_table(
    table_id
)

print(
    f"Loaded rows: {table.num_rows:,}"
)


# ---------------------------------------------------------
# VALIDATION QUERY
# ---------------------------------------------------------

query = f"""
SELECT
    COUNT(*) AS total_records,

    COUNT(DISTINCT site_id)
        AS total_sites,

    COUNTIF(
        severity = 'WARNING'
    ) AS warning_samples,

    COUNTIF(
        severity = 'CRITICAL'
    ) AS critical_samples,

    ROUND(
        AVG(latency_ms),
        2
    ) AS avg_latency_ms

FROM `{table_id}`
"""


rows = list(
    client.query(query).result()
)

result = rows[0]


print()
print(
    "NETWORKOPS BIGQUERY VALIDATION"
)
print(
    "----------------------------"
)

print(
    f"Records   : "
    f"{result.total_records:,}"
)

print(
    f"Sites     : "
    f"{result.total_sites}"
)

print(
    f"Warnings  : "
    f"{result.warning_samples:,}"
)

print(
    f"Critical  : "
    f"{result.critical_samples:,}"
)

print(
    f"Avg Latency: "
    f"{result.avg_latency_ms} ms"
)