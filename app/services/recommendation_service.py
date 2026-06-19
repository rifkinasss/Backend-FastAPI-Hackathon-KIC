RECOMMENDATIONS = {
    "pm25": {
        "Bahaya": "Kurangi aktivitas area tambang, aktifkan water spray, dan gunakan APD respirator.",
        "Waspada": "Pantau kadar debu dan siapkan penyiraman area operasional.",
    },
    "pm10": {
        "Bahaya": "Kurangi aktivitas pengangkutan, aktifkan water spray, dan batasi paparan pekerja.",
        "Waspada": "Pantau debu kasar dan lakukan penyiraman jalur tambang.",
    },
    "co": {
        "Bahaya": "Evakuasi area dan hentikan operasi alat berat sampai kadar CO turun.",
        "Waspada": "Periksa pembakaran mesin dan tingkatkan ventilasi area kerja.",
    },
    "co2": {
        "Bahaya": "Evakuasi area, tingkatkan ventilasi, dan lakukan inspeksi sumber emisi.",
        "Waspada": "Pantau ventilasi dan kurangi sumber emisi sementara.",
    },
    "h2s": {
        "Bahaya": "Evakuasi area dan aktifkan ventilasi darurat.",
        "Waspada": "Tingkatkan ventilasi dan siapkan pemeriksaan kebocoran gas.",
    },
    "ch4": {
        "Bahaya": "Hentikan aktivitas, jauhkan sumber api, dan lakukan pemeriksaan kebocoran CH4.",
        "Waspada": "Pantau konsentrasi CH4 dan siapkan ventilasi tambahan.",
    },
    "suhu": {
        "Bahaya": "Kurangi paparan panas dan atur rotasi kerja.",
        "Waspada": "Pantau suhu area dan siapkan pendinginan/istirahat kerja.",
    },
    "kelembaban": {
        "Bahaya": "Evaluasi kondisi lingkungan dan batasi aktivitas jika mengganggu keselamatan.",
        "Waspada": "Pantau kelembaban karena dapat memengaruhi kualitas udara dan kenyamanan kerja.",
    },
}


def incident_recommendation(param, level):
    return RECOMMENDATIONS.get(param, {}).get(
        level,
        "Pantau kondisi sensor dan lakukan pemeriksaan lapangan.",
    )

