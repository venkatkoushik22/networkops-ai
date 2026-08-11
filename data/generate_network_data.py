import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


OUTPUT_FILE = Path(__file__).parent / "network_telemetry.csv"

NUM_SITES = 50
DAYS = 7
INTERVAL_MINUTES = 15


MARKETS = {
    "Hoboken": {
        "code": "HOB",
        "region": "North Jersey",
        "weight": 7,
    },
    "Jersey City": {
        "code": "JCY",
        "region": "North Jersey",
        "weight": 10,
    },
    "Newark": {
        "code": "NWK",
        "region": "North Jersey",
        "weight": 10,
    },
    "Paterson": {
        "code": "PAT",
        "region": "North Jersey",
        "weight": 6,
    },
    "Secaucus": {
        "code": "SEC",
        "region": "North Jersey",
        "weight": 6,
    },
    "Elizabeth": {
        "code": "ELZ",
        "region": "North Jersey",
        "weight": 6,
    },
    "Edison": {
        "code": "EDI",
        "region": "Central Jersey",
        "weight": 8,
    },
    "New Brunswick": {
        "code": "NBR",
        "region": "Central Jersey",
        "weight": 7,
    },
    "Princeton": {
        "code": "PRI",
        "region": "Central Jersey",
        "weight": 5,
    },
    "Trenton": {
        "code": "TRE",
        "region": "Central Jersey",
        "weight": 5,
    },
}


def choose_market():
    cities = list(MARKETS.keys())
    weights = [MARKETS[city]["weight"] for city in cities]

    city = random.choices(
        cities,
        weights=weights,
        k=1,
    )[0]

    return city, MARKETS[city]


def generate_site(site_number):
    city, market = choose_market()

    technology = random.choices(
        ["5G", "LTE"],
        weights=[72, 28],
        k=1,
    )[0]

    capacity = random.choices(
        [500, 1000, 2000, 5000],
        weights=[10, 35, 40, 15],
        k=1,
    )[0]

    return {
        "site_id": f"NJ-{market['code']}-{site_number:03d}",
        "city": city,
        "region": market["region"],
        "technology": technology,
        "bandwidth_mbps": capacity,
    }


def traffic_profile(hour):
    if 0 <= hour < 6:
        return 18, 38

    if 6 <= hour < 9:
        return 35, 58

    if 9 <= hour < 16:
        return 48, 72

    if 16 <= hour < 21:
        return 60, 84

    return 38, 62


def generate_normal_metrics(site, timestamp):
    low, high = traffic_profile(timestamp.hour)

    utilization = random.uniform(low, high)

    latency_base = (
        18
        if site["technology"] == "5G"
        else 28
    )

    latency = random.uniform(
        latency_base,
        latency_base + 18,
    )

    packet_loss = random.uniform(0.01, 0.55)

    availability = random.uniform(
        99.92,
        100.0,
    )

    active_users = int(
        utilization
        * random.uniform(9, 18)
    )

    return (
        utilization,
        latency,
        packet_loss,
        availability,
        active_users,
    )


def inject_event(
    utilization,
    latency,
    packet_loss,
    availability,
):
    event_roll = random.random()

    alarm_code = "NO_ALARM"
    severity = "NORMAL"
    incident_status = "CLEAR"

    if event_roll < 0.004:
        utilization = random.uniform(93, 99)
        latency = random.uniform(110, 190)
        packet_loss = random.uniform(7, 14)
        availability = random.uniform(95.5, 98.5)

        alarm_code = "TRANSPORT_LINK_FAILURE"
        severity = "CRITICAL"
        incident_status = "OPEN"

    elif event_roll < 0.009:
        utilization = random.uniform(90, 98)
        latency = random.uniform(85, 145)
        packet_loss = random.uniform(3, 8)

        alarm_code = "CAPACITY_CONGESTION"
        severity = "CRITICAL"
        incident_status = "INVESTIGATING"

    elif event_roll < 0.017:
        latency = random.uniform(70, 115)
        packet_loss = random.uniform(1.5, 4.5)

        alarm_code = "TRANSPORT_DEGRADATION"
        severity = "WARNING"
        incident_status = "MONITORING"

    elif utilization > 80:
        alarm_code = "HIGH_UTILIZATION"
        severity = "WARNING"
        incident_status = "MONITORING"

    return (
        utilization,
        latency,
        packet_loss,
        availability,
        alarm_code,
        severity,
        incident_status,
    )


def calculate_health(
    utilization,
    latency,
    packet_loss,
    availability,
):
    score = 100.0

    score -= max(
        0,
        utilization - 72,
    ) * 0.42

    score -= max(
        0,
        latency - 40,
    ) * 0.18

    score -= packet_loss * 2.6

    score -= max(
        0,
        99.9 - availability,
    ) * 6.5

    return round(
        max(0, min(100, score)),
        2,
    )


def generate_metrics(site, timestamp):
    (
        utilization,
        latency,
        packet_loss,
        availability,
        active_users,
    ) = generate_normal_metrics(
        site,
        timestamp,
    )

    (
        utilization,
        latency,
        packet_loss,
        availability,
        alarm_code,
        severity,
        incident_status,
    ) = inject_event(
        utilization,
        latency,
        packet_loss,
        availability,
    )

    throughput = (
        site["bandwidth_mbps"]
        * utilization
        / 100
        * random.uniform(
            0.80,
            0.96,
        )
    )

    health_score = calculate_health(
        utilization,
        latency,
        packet_loss,
        availability,
    )

    return {
        "timestamp": timestamp.isoformat(),
        "site_id": site["site_id"],
        "city": site["city"],
        "region": site["region"],
        "technology": site["technology"],
        "bandwidth_mbps": site["bandwidth_mbps"],
        "active_users": active_users,
        "utilization_pct": round(utilization, 2),
        "throughput_mbps": round(throughput, 2),
        "latency_ms": round(latency, 2),
        "packet_loss_pct": round(packet_loss, 2),
        "availability_pct": round(availability, 4),
        "health_score": health_score,
        "alarm_type": alarm_code,
        "severity": severity,
        "incident_status": incident_status,
    }


def main():
    random.seed(42)

    sites = [
        generate_site(i)
        for i in range(1, NUM_SITES + 1)
    ]

    end_time = datetime.now().replace(
        second=0,
        microsecond=0,
    )

    start_time = (
        end_time
        - timedelta(days=DAYS)
    )

    rows = []

    current = start_time

    while current <= end_time:
        for site in sites:
            rows.append(
                generate_metrics(
                    site,
                    current,
                )
            )

        current += timedelta(
            minutes=INTERVAL_MINUTES
        )

    fieldnames = list(
        rows[0].keys()
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    critical = sum(
        row["severity"] == "CRITICAL"
        for row in rows
    )

    warnings = sum(
        row["severity"] == "WARNING"
        for row in rows
    )

    print()
    print("NETWORKOPS TELEMETRY GENERATION COMPLETE")
    print("----------------------------------------")
    print(f"Sites             : {NUM_SITES}")
    print(f"Observation window: {DAYS} days")
    print(f"Interval          : {INTERVAL_MINUTES} min")
    print(f"Telemetry records : {len(rows):,}")
    print(f"Critical samples  : {critical:,}")
    print(f"Warning samples   : {warnings:,}")
    print(f"Output            : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
