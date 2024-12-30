from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone
import os

bucket = os.getenv('INFLUXDB_V2_BUCKET')

client = InfluxDBClient.from_env_properties()

write_api = client.write_api(write_options=SYNCHRONOUS)


def write_current_status(status):
    points = []

    for field in [
        "deiceStatus",
        "operationStatus",
        "operationMode",
        "modelSeriesSelection",
        "waterPressure",
        "cnCntErrorStatus",
        "outdoorNow",
        "holidayTimer",
        "powerful",
        "electricAnode",
        "bivalent",
        "informationMessage",
        "pumpDuty",
        "quietMode",
        "forceHeater",
        "tank",
        "forceDHW",
        "pendingUser",
        "direction",
    ]:
        if status[field] is not None:
            points.append(
                Point("heatpump").field(
                    field.replace("deiceStatus", "deviceStatus"), float(status[field])
                )
            )

    for i, tank in enumerate(status["tankStatus"]):
        for field in [
            "operationStatus",
            "temparatureNow",
            "heatMax",
            "heatMin",
            "heatSet",
        ]:
            if tank[field] is not None:
                points.append(
                    Point("heatpump").field(f"tank_{i+1}_{field}", float(tank[field]))
                )

    for zone in status["zoneStatus"]:
        for field in [
            "operationStatus",
            "ecoHeat",
            "coolMin",
            "heatMin",
            "comfortCool",
            "temparatureNow",
            "coolSet",
            "comfortHeat",
            "heatMax",
            "coolMax",
            "ecoCool",
            "heatSet",
        ]:
            if zone[field] is not None:
                points.append(
                    Point("heatpump").field(
                        f"zone_{zone['zoneId']}_{field}", float(zone[field])
                    )
                )

    write_api.write(bucket=bucket, record=points)


def write_consumption_data(consumption, date: str):
    points = []

    for dataset in consumption:
        dataset_name = dataset["name"]
        for record in dataset["data"]:
            record_name = record["name"]
            for i, hour_value in enumerate(record["values"]):
                if hour_value is not None:
                    ts = datetime.strptime(f"{date}-{i}", "%Y-%m-%d-%H").replace(
                        tzinfo=timezone.utc
                    )
                    points.append(
                        Point("heatpump")
                        .field(f"{dataset_name}_{record_name}", float(hour_value))
                        .time(ts)
                    )

    write_api.write(bucket=bucket, record=points)


def contains_any_consumption_data(consumption):
    for dataset in consumption:
        for record in dataset["data"]:
            for hour_value in record["values"]:
                if hour_value is not None:
                    return True
    return False
