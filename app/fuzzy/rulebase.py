def evaluasi_rulebase(derajat_vars, kategori):
    status_final = "AMAN"

    if kategori == "DEBU TAMBANG":
        pm25 = derajat_vars.get("PM25", {"Tinggi": 0, "Sedang": 0})
        pm10 = derajat_vars.get("PM10", {"Tinggi": 0, "Sedang": 0})
        suhu = derajat_vars.get("SUHU", {"Tinggi": 0})

        if pm25["Tinggi"] > 0.7 or pm10["Tinggi"] > 0.7:
            status_final = "BAHAYA (Kadar Debu Sangat Tinggi)"
        elif (pm25["Sedang"] > 0.5 or pm10["Sedang"] > 0.5) and suhu["Tinggi"] > 0.5:
            status_final = "BAHAYA (Debu Kering & Beresiko)"
        elif pm25["Sedang"] > 0.3 or pm10["Sedang"] > 0.3:
            status_final = "WASPADA (Peningkatan Partikel)"

    elif kategori == "GAS TAMBANG":
        h2s = derajat_vars.get("H2S", {"Tinggi": 0, "Sedang": 0})
        ch4 = derajat_vars.get("CH4", {"Tinggi": 0, "Sedang": 0})

        if h2s["Tinggi"] > 0.01:
            status_final = "BAHAYA (Terdeteksi Gas Beracun H2S)"
        elif ch4["Tinggi"] > 0.5:
            status_final = "BAHAYA (Resiko Ledakan CH4)"
        elif ch4["Sedang"] > 0.5 or h2s["Sedang"] > 0.5:
            status_final = "WASPADA (Kebocoran Gas Ringan)"

    elif kategori == "EMISI ALAT BERAT":
        co = derajat_vars.get("CO", {"Tinggi": 0, "Sedang": 0})
        co2 = derajat_vars.get("CO2", {"Tinggi": 0, "Sedang": 0})

        if co["Tinggi"] > 0.4:
            status_final = "BAHAYA (Emisi CO Tinggi)"
        elif co2["Tinggi"] > 0.6:
            status_final = "BAHAYA (Kadar CO2 Melampaui Batas)"
        elif co["Sedang"] > 0.4 or co2["Sedang"] > 0.4:
            status_final = "WASPADA (Emisi Mesin Tidak Normal)"

    return status_final

