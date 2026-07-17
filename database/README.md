# Database

Folder ini berisi file database backend.

## File

- `schema.sql` - schema PostgreSQL utama untuk device, sensor, readings, dan hasil klasifikasi fuzzy.

## Struktur Utama

```text
devices
  Master data device: device_id, device_name, lokasi, deskripsi, dan timestamp.

sensors
  Master data alat/sensor, termasuk latitude dan longitude untuk marker dashboard.

tb_debu_tambang
  Data pembacaan debu tambang: pm25, pm10, suhu, kelembaban.

tb_gas_tambang
  Data pembacaan gas tambang: ch4, h2s, suhu, kelembaban.

tb_emisi_alat_berat
  Data pembacaan emisi alat berat: co, co2, suhu, kelembaban.

classifications
  Hasil fuzzy/AI dari salah satu tabel readings.

dht22_readings
  Data pembacaan DHT22: device_id, suhu Celsius, kelembaban persen, dan waktu pembacaan.
```

## Cara Import

```bash
createdb iot_fuzzy_kideco
psql -d iot_fuzzy_kideco -f database/schema.sql
```

Untuk import CSV dummy ke PostgreSQL:

```bash
python import_csv_to_postgresql.py
```

## Catatan Lokasi

Dashboard map marker cukup memakai:

```text
latitude, longitude
```

Format frontend seperti Leaflet biasanya:

```js
L.marker([sensor.latitude, sensor.longitude])
```
# Provisioning perangkat otomatis

Untuk database yang sudah dibuat sebelum fitur provisioning, jalankan sekali:

```bash
psql -d iot_fuzzy_kideco -f migrations/20260717_device_provisioning.sql
```

Setelah firmware `simosi_esp32.ino` versi 1.3 di-flash dan tersambung Wi-Fi,
ESP32 akan mengirim MAC address, versi firmware, serta sensor yang terpasang ke
`POST /api/v1/devices/provision`. Backend membuat device baru dengan status
`pending`; operator harus melengkapi lokasi lalu menyetujui perangkat melalui:

```http
PUT /api/v1/devices/{device_id}/provisioning
Content-Type: application/json

{"status":"approved"}
```

Perangkat akan mengulangi provisioning setiap interval sampai statusnya
`approved`, lalu baru mengirim pembacaan sensor.

