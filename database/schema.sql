-- PostgreSQL schema for the IoT Fuzzy Kideco backend.
-- Create the database first when needed:
--   createdb iot_fuzzy_kideco

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL UNIQUE,
    device_name VARCHAR(100),
    location VARCHAR(150),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_devices_updated_at ON devices;
CREATE TRIGGER trg_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS sensors (
    id BIGSERIAL PRIMARY KEY,
    sensor_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    location_name VARCHAR(150),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_sensors_updated_at ON sensors;
CREATE TRIGGER trg_sensors_updated_at
    BEFORE UPDATE ON sensors
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_sensors_category ON sensors (category);
CREATE INDEX IF NOT EXISTS idx_sensors_status ON sensors (status);
CREATE INDEX IF NOT EXISTS idx_sensors_location ON sensors (latitude, longitude);

CREATE TABLE IF NOT EXISTS tb_debu_tambang (
    id BIGSERIAL PRIMARY KEY,
    waktu TIMESTAMP NOT NULL,
    sensor_id VARCHAR(100) NOT NULL,
    lokasi VARCHAR(150),
    pm25 NUMERIC(10, 2),
    pm10 NUMERIC(10, 2),
    suhu NUMERIC(10, 2),
    kelembaban NUMERIC(10, 2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tb_debu_tambang_sensor_time
    ON tb_debu_tambang (sensor_id, waktu);
CREATE INDEX IF NOT EXISTS idx_tb_debu_tambang_time
    ON tb_debu_tambang (waktu);

CREATE TABLE IF NOT EXISTS tb_gas_tambang (
    id BIGSERIAL PRIMARY KEY,
    waktu TIMESTAMP NOT NULL,
    sensor_id VARCHAR(100) NOT NULL,
    lokasi VARCHAR(150),
    ch4 NUMERIC(10, 2),
    h2s NUMERIC(10, 2),
    suhu NUMERIC(10, 2),
    kelembaban NUMERIC(10, 2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tb_gas_tambang_sensor_time
    ON tb_gas_tambang (sensor_id, waktu);
CREATE INDEX IF NOT EXISTS idx_tb_gas_tambang_time
    ON tb_gas_tambang (waktu);

CREATE TABLE IF NOT EXISTS tb_emisi_alat_berat (
    id BIGSERIAL PRIMARY KEY,
    waktu TIMESTAMP NOT NULL,
    sensor_id VARCHAR(100) NOT NULL,
    lokasi VARCHAR(150),
    co NUMERIC(10, 2),
    co2 NUMERIC(10, 2),
    suhu NUMERIC(10, 2),
    kelembaban NUMERIC(10, 2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tb_emisi_alat_berat_sensor_time
    ON tb_emisi_alat_berat (sensor_id, waktu);
CREATE INDEX IF NOT EXISTS idx_tb_emisi_alat_berat_time
    ON tb_emisi_alat_berat (waktu);

CREATE TABLE IF NOT EXISTS dht22_readings (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL,
    temperature_c NUMERIC(5, 2) NOT NULL,
    humidity_percent NUMERIC(5, 2) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_dht22_readings_device
        FOREIGN KEY (device_id) REFERENCES devices(device_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_dht22_temperature
        CHECK (temperature_c BETWEEN -40 AND 80),
    CONSTRAINT chk_dht22_humidity
        CHECK (humidity_percent BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_dht22_readings_device_time
    ON dht22_readings (device_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS device_states (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL UNIQUE,
    is_online BOOLEAN NOT NULL DEFAULT TRUE,
    power_state VARCHAR(20) NOT NULL DEFAULT 'on',
    last_seen_at TIMESTAMPTZ,
    last_command_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_device_states_device
        FOREIGN KEY (device_id) REFERENCES devices(device_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_device_states_online
    ON device_states (is_online);
CREATE INDEX IF NOT EXISTS idx_device_states_last_seen
    ON device_states (last_seen_at);

CREATE TABLE IF NOT EXISTS device_commands (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL,
    command VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    requested_by VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    CONSTRAINT fk_device_commands_device
        FOREIGN KEY (device_id) REFERENCES devices(device_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT chk_device_commands_command
        CHECK (command IN ('turn_off', 'turn_on', 'restart')),
    CONSTRAINT chk_device_commands_status
        CHECK (status IN ('pending', 'sent', 'acknowledged', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_device_commands_device_status
    ON device_commands (device_id, status);
CREATE INDEX IF NOT EXISTS idx_device_commands_created
    ON device_commands (created_at);

CREATE TABLE IF NOT EXISTS classifications (
    id BIGSERIAL PRIMARY KEY,
    sensor_id BIGINT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_reading_id BIGINT NOT NULL,
    classification VARCHAR(100) NOT NULL,
    risk_level VARCHAR(30) NOT NULL,
    score NUMERIC(10, 2),
    message TEXT,
    rule_version VARCHAR(50) DEFAULT 'v1',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_classifications_sensor
        FOREIGN KEY (sensor_id) REFERENCES sensors(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_classifications_sensor_created
    ON classifications (sensor_id, created_at);
CREATE INDEX IF NOT EXISTS idx_classifications_source
    ON classifications (source_type, source_reading_id);
CREATE INDEX IF NOT EXISTS idx_classifications_risk
    ON classifications (risk_level);
CREATE INDEX IF NOT EXISTS idx_classifications_created
    ON classifications (created_at);

INSERT INTO sensors (
    sensor_code,
    name,
    category,
    location_name,
    latitude,
    longitude
) VALUES
    ('DB001', 'Sensor Debu Jalan Tambang A', 'dust', 'Jalan Tambang A', -1.8542000, 116.2156000),
    ('GS001', 'Sensor Gas Area Dasar Tambang', 'gas', 'Area Dasar Tambang', -1.8612000, 116.2234000),
    ('EM001', 'Sensor Emisi Bengkel Alat Berat', 'heavy_equipment', 'Bengkel Alat Berat', -1.8485000, 116.2089000)
ON CONFLICT (sensor_code) DO UPDATE SET
    name = EXCLUDED.name,
    category = EXCLUDED.category,
    location_name = EXCLUDED.location_name,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    updated_at = CURRENT_TIMESTAMP;
