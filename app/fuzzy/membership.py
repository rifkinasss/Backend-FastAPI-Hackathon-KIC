import numpy as np
import skfuzzy as fuzz

from app.fuzzy.config import konfigurasi_fuzzy


def generate_membership_data():
    membership_data = {}

    for var, cfg in konfigurasi_fuzzy.items():
        x_range = np.arange(cfg["rentang"][0], cfg["rentang"][1], cfg["rentang"][2])
        t1, t2 = cfg["batas_titik"]
        v_max = cfg["rentang"][1]

        lo = fuzz.trapmf(x_range, [0, 0, 0, t1])
        md = fuzz.trimf(x_range, [0, t1, t2])
        hi = fuzz.trapmf(x_range, [t1, t2, v_max, v_max])

        membership_data[var] = {"x": x_range, "lo": lo, "md": md, "hi": hi}

    return membership_data


mf_data = generate_membership_data()


def kalkulasi_fuzzifikasi(nilai, var_name):
    if var_name not in mf_data:
        return {"Rendah": 0, "Sedang": 0, "Tinggi": 0}

    mf = mf_data[var_name]
    x_range = mf["x"]

    nilai_safe = np.clip(nilai, x_range[0], x_range[-1])

    d_rendah = fuzz.interp_membership(x_range, mf["lo"], nilai_safe)
    d_sedang = fuzz.interp_membership(x_range, mf["md"], nilai_safe)
    d_tinggi = fuzz.interp_membership(x_range, mf["hi"], nilai_safe)

    return {
        "Rendah": round(float(d_rendah), 2),
        "Sedang": round(float(d_sedang), 2),
        "Tinggi": round(float(d_tinggi), 2),
    }


def available_fuzzy_params(df):
    return [column for column in df.select_dtypes(include="number").columns if column in mf_data]


def parameter_level(value, param):
    derajat = kalkulasi_fuzzifikasi(value, param)
    if derajat["Tinggi"] >= 0.7:
        return "Bahaya", derajat
    if derajat["Tinggi"] >= 0.3 or derajat["Sedang"] >= 0.5:
        return "Waspada", derajat
    return "Aman", derajat

