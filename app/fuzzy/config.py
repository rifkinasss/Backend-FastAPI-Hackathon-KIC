# Fuzzy configuration follows the existing notebook/backend thresholds.
konfigurasi_fuzzy = {
    "pm25": {
        "nama": "PM2.5 (Debu Halus)",
        "rentang": [0, 81, 0.5],
        "batas_titik": [27.5, 55],
    },
    "pm10": {
        "nama": "PM10 (Debu Kasar)",
        "rentang": [0, 111, 0.5],
        "batas_titik": [37.5, 75],
    },
    "co": {
        "nama": "CO (Karbon Monoksida)",
        "rentang": [0, 15001, 10],
        "batas_titik": [5000, 10000],
    },
    "co2": {
        "nama": "CO2 (Karbon Dioksida)",
        "rentang": [0, 7501, 10],
        "batas_titik": [2500, 5000],
    },
    "h2s": {
        "nama": "H2S (Hidrogen Sulfida)",
        "rentang": [0, 1.6, 0.01],
        "batas_titik": [0.5, 1],
    },
    "ch4": {
        "nama": "CH4 (Metana)",
        "rentang": [0, 15001, 10],
        "batas_titik": [5000, 10000],
    },
    "h2": {
        "nama": "H2 (Hidrogen)",
        "rentang": [0, 12501, 10],
        "batas_titik": [4100, 8200],
    },
    "suhu": {
        "nama": "Suhu Lingkungan (°C)",
        "rentang": [0, 41, 0.5],
        "batas_titik": [24, 32],
    },
    "kelembaban": {
        "nama": "Kelembaban Udara (%)",
        "rentang": [0, 101, 1],
        "batas_titik": [40, 70],
    },
}

