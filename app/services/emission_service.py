import pandas as pd

from app.core.config import DATASET_FILES
from app.data.loaders import read_full_csv_dataset
from app.fuzzy.membership import available_fuzzy_params, parameter_level
from app.services.recommendation_service import incident_recommendation


def parse_window(window):
    if not window:
        return pd.Timedelta(minutes=30)

    value = str(window).strip().lower()
    if value.endswith("m"):
        return pd.Timedelta(minutes=int(value[:-1]))
    if value.endswith("h"):
        return pd.Timedelta(hours=int(value[:-1]))
    if value.endswith("d"):
        return pd.Timedelta(days=int(value[:-1]))

    raise ValueError("Unsupported window format. Use values like 30m, 1h, or 1d.")


def status_from_counts(danger_count, warning_count):
    if danger_count > 0:
        return "danger"
    if warning_count > 0:
        return "warning"
    return "safe"


def get_emission_alert(window="30m"):
    window_delta = parse_window(window)
    latest_time = max(read_full_csv_dataset(name)["waktu"].max() for name in DATASET_FILES)
    start_time = latest_time - window_delta
    incidents = []

    for dataset_name in DATASET_FILES:
        df = read_full_csv_dataset(dataset_name)
        df_window = df[(df["waktu"] > start_time) & (df["waktu"] <= latest_time)]
        params = available_fuzzy_params(df_window)

        for _, row in df_window.iterrows():
            for param in params:
                level, _ = parameter_level(row[param], param)
                if level not in {"Bahaya", "Waspada"}:
                    continue

                incidents.append({
                    "dataset": dataset_name,
                    "time": row["waktu"].strftime("%Y-%m-%d %H:%M:%S"),
                    "sensor_id": str(row.get("sensor_id", "")),
                    "location": str(row.get("lokasi", "")),
                    "parameter": param.upper(),
                    "value": round(float(row[param]), 3),
                    "level": level,
                    "recommendation": incident_recommendation(param, level),
                })

    danger_count = sum(1 for incident in incidents if incident["level"] == "Bahaya")
    warning_count = sum(1 for incident in incidents if incident["level"] == "Waspada")
    status = status_from_counts(danger_count, warning_count)

    if danger_count:
        summary = f"Terdapat {danger_count} kondisi bahaya dalam {window} terakhir."
    elif warning_count:
        summary = f"Terdapat {warning_count} kondisi waspada dalam {window} terakhir."
    else:
        summary = f"Tidak terdapat kondisi bahaya atau waspada dalam {window} terakhir."

    return {
        "status": status,
        "should_alert": danger_count > 0,
        "window": window,
        "incidents": incidents,
        "summary": summary,
    }


def get_daily_emission_report(report_date=None):
    if report_date:
        target_date = pd.to_datetime(report_date).date()
    else:
        target_date = max(read_full_csv_dataset(name)["waktu"].max() for name in DATASET_FILES).date()

    datasets = {}
    recommendations = []
    total_danger = 0
    total_warning = 0

    for dataset_name in DATASET_FILES:
        df = read_full_csv_dataset(dataset_name)
        df_day = df[df["waktu"].dt.date == target_date]
        params = available_fuzzy_params(df_day)
        dataset_danger = 0
        dataset_warning = 0
        parameter_summary = {}

        for param in params:
            values = df_day[param].dropna()
            if values.empty:
                continue

            levels = [parameter_level(value, param)[0] for value in values]
            danger_count = levels.count("Bahaya")
            warning_count = levels.count("Waspada")
            dataset_danger += danger_count
            dataset_warning += warning_count

            parameter_summary[param.upper()] = {
                "min": round(float(values.min()), 3),
                "max": round(float(values.max()), 3),
                "avg": round(float(values.mean()), 3),
                "danger_count": danger_count,
                "warning_count": warning_count,
            }

            if danger_count:
                recommendations.append(incident_recommendation(param, "Bahaya"))
            elif warning_count:
                recommendations.append(incident_recommendation(param, "Waspada"))

        total_danger += dataset_danger
        total_warning += dataset_warning
        datasets[dataset_name] = {
            "rows": int(len(df_day)),
            "status": status_from_counts(dataset_danger, dataset_warning),
            "danger_count": dataset_danger,
            "warning_count": dataset_warning,
            "parameters": parameter_summary,
        }

    if total_danger:
        summary = f"Kualitas udara berbahaya, terdapat {total_danger} kejadian bahaya dan {total_warning} kejadian waspada."
    elif total_warning:
        summary = f"Kualitas udara relatif aman, terdapat {total_warning} kejadian waspada."
    else:
        summary = "Kualitas udara aman, tidak terdapat kejadian bahaya atau waspada."

    return {
        "date": target_date.isoformat(),
        "summary": summary,
        "datasets": datasets,
        "recommendations": sorted(set(recommendations)),
    }

