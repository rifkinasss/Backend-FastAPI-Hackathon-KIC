import pandas as pd

from app.data.loaders import latest_timestamp, load_datasets
from app.fuzzy.membership import available_fuzzy_params, kalkulasi_fuzzifikasi, mf_data
from app.fuzzy.rulebase import evaluasi_rulebase


def hit_rata_rata(data, start_date=None, end_date=None):
    df = data.copy()

    if "sensor_id" in df.columns:
        df["sensor_id"] = df["sensor_id"].astype(str).str.strip()

    if not pd.api.types.is_datetime64_any_dtype(df["waktu"]):
        df["waktu"] = pd.to_datetime(df["waktu"])

    if start_date and end_date:
        mask = (df["waktu"] >= pd.to_datetime(start_date)) & (df["waktu"] <= pd.to_datetime(end_date))
        df = df.loc[mask]

    if df.empty:
        return None

    kolom_numerik = df.select_dtypes(include="number").columns
    return df.groupby("sensor_id")[kolom_numerik].mean().round(2)


def get_analysis(start_date=None, end_date=None):
    if start_date and end_date:
        is_manual_filter = True
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        fetch_start = start_dt
        fetch_end = end_dt
    else:
        is_manual_filter = False
        latest_ref = latest_timestamp()
        if latest_ref is None:
            return {}

        end_dt = pd.to_datetime(latest_ref)
        start_dt = end_dt - pd.Timedelta(minutes=30)
        fetch_start = end_dt - pd.Timedelta(hours=24)
        fetch_end = end_dt

    datasets = load_datasets(fetch_start, fetch_end)
    final_results = {}

    for kategori, df_mentah in datasets.items():
        if df_mentah.empty:
            final_results[kategori] = []
            continue

        if is_manual_filter:
            df_snapshot = df_mentah
            info_text = f"Mean Filter: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
            window_label = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
        else:
            df_snapshot = df_mentah[df_mentah["waktu"] >= start_dt]
            info_text = "Rata-rata 30 Menit (Realtime)"
            window_label = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"

        df_avg = hit_rata_rata(df_snapshot)

        if df_avg is None:
            final_results[kategori] = []
            continue

        kategori_data = []
        for sensor_id, row in df_avg.iterrows():
            derajat_sensor = {}
            param_details = []
            available_params = [p for p in df_avg.columns if p in mf_data]

            for param in available_params:
                if pd.isna(row[param]):
                    continue

                derajat = kalkulasi_fuzzifikasi(row[param], param)
                derajat_sensor[param.upper()] = derajat
                param_details.append({
                    "param": param.upper(),
                    "nilai": round(row[param], 2),
                    "derajat": derajat,
                    "info": info_text,
                })

            history_df = df_mentah[df_mentah["sensor_id"] == sensor_id].sort_values("waktu")
            history_list = []

            for _, h_row in history_df.iterrows():
                h_time = h_row["waktu"]
                h_window_start = h_time - pd.Timedelta(minutes=30)
                h_window_df = history_df[(history_df["waktu"] > h_window_start) & (history_df["waktu"] <= h_time)]
                h_avg = h_window_df[available_params].mean()

                h_derajat_total = []
                for param in available_params:
                    if pd.isna(h_avg[param]):
                        continue

                    derajat = kalkulasi_fuzzifikasi(h_avg[param], param)
                    h_derajat_total.append(derajat["Tinggi"])

                crisp_val = (sum(h_derajat_total) / len(h_derajat_total)) * 100 if h_derajat_total else 0

                history_list.append({
                    "timestamp": h_time.strftime("%H:%M"),
                    "crisp": round(float(crisp_val), 2),
                    "is_averaged": len(h_window_df) > 1,
                })

            keputusan = evaluasi_rulebase(derajat_sensor, kategori)
            lokasi = str(df_mentah[df_mentah["sensor_id"] == sensor_id]["lokasi"].iloc[0])
            kategori_data.append({
                "sensor_id": sensor_id,
                "lokasi": lokasi,
                "params": param_details,
                "status": keputusan,
                "latest_window": window_label,
                "history": history_list,
            })

        final_results[kategori] = kategori_data

    return final_results

