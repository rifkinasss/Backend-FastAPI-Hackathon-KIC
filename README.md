# Backend

Backend FastAPI untuk dashboard IoT fuzzy.

## Struktur Folder

```text
backend/
  main.py                       Entry point FastAPI dan router registration
  fuzzy_engine.py               Compatibility wrapper untuk import lama
  import_csv_to_postgresql.py   Import CSV dummy ke PostgreSQL
  expand_csv_dummy_data.py      Generate/expand data dummy CSV
  requirements.txt              Dependency Python backend
  app/
    core/                       Konfigurasi environment dan PostgreSQL
    data/                       Loader data dan normalisasi dataframe
    fuzzy/                      Konfigurasi fuzzy, membership, dan rulebase
    models/                     SQLModel untuk tabel PostgreSQL
    routes/                     Router FastAPI
    services/                   Logic analisis, DHT22, emisi, dan rekomendasi
  database/
    schema.sql                  Schema PostgreSQL utama
    README.md                   Catatan database
```

## Jalankan API di Windows PowerShell

Masuk ke folder backend:

```powershell
cd "C:\Tanamin Bumi Nusantara\Lomba\iot-fuzzy\dashboard-iot-fuzzy\backend"
```

Buat virtual environment baru jika belum ada:

```powershell
python -m venv .venv
```

Aktifkan virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependency:

```powershell
python -m pip install -r requirements.txt
```

Jalankan API:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Alternatif tanpa activate:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Backend berjalan di:

```text
http://127.0.0.1:8000
```

Swagger/OpenAPI:

```text
http://127.0.0.1:8000/docs
```

## Setup Database PostgreSQL

Isi credential PostgreSQL di `.env`:

```env
IOT_FUZZY_DATA_SOURCE=postgresql
DB_USERNAME=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=iot_fuzzy_kideco
IOT_FUZZY_AUTO_CREATE_TABLES=false
```

Buat database, lalu jalankan schema:

```powershell
createdb iot_fuzzy_kideco
psql -d iot_fuzzy_kideco -f database/schema.sql
```

Import CSV dummy ke PostgreSQL:

```powershell
python import_csv_to_postgresql.py
```

## Cek API

```powershell
curl.exe http://127.0.0.1:8000/
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/analysis
curl.exe http://127.0.0.1:8000/config
```

Output normal untuk `/`:

```json
{"status":"API is running"}
```

## Endpoint DHT22 dengan PostgreSQL

Endpoint DHT22 otomatis muncul di Swagger/OpenAPI. Setiap data DHT22 disimpan sebagai log asli di `dht22_readings`, lalu dicerminkan ke `tb_debu_tambang`, `tb_gas_tambang`, dan `tb_emisi_alat_berat` pada kolom `suhu` dan `kelembaban`.

Kirim data sensor:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/sensors/dht22/readings `
  -H "Content-Type: application/json" `
  -d '{"device_id":"DHT22-001","device_name":"DHT 22 Greenhouse 1","location":"Greenhouse A","temperature":29.4,"humidity":72.8}'
```

Field yang diterima:

```json
{
  "device_id": "DHT22-001",
  "device_name": "DHT 22 Greenhouse 1",
  "location": "Greenhouse A",
  "description": "Sensor suhu dan kelembaban area greenhouse",
  "temperature": 29.4,
  "humidity": 72.8,
  "recorded_at": "2026-06-17T08:00:00Z"
}
```

## Bersihkan dan Buat Ulang Virtual Environment

Project ini memakai satu virtual environment saja: `.venv`.

Jika perlu buat ulang dari nol:

```powershell
cd "C:\Tanamin Bumi Nusantara\Lomba\iot-fuzzy\dashboard-iot-fuzzy\backend"
Remove-Item -LiteralPath .venv -Recurse -Force
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
