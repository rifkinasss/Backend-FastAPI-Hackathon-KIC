-- ============================================================
-- SIMOSI — Smart IoT Monitoring System
-- PostgreSQL Schema v2.0
-- ============================================================
-- Target  : PostgreSQL 15+
-- Stack   : FastAPI · SQLAlchemy · ESP32 · Next.js
-- Domain  : Environmental monitoring for mining operations
-- Pattern : Header-Detail (sensor_readings → detail tables)
-- ============================================================
-- Usage   : psql -U postgres -d simosi -f schema.sql
-- ============================================================

-- ************************************************************
-- 0. CLEAN SLATE (Drops old tables/views)
-- ************************************************************

DROP VIEW IF EXISTS vw_dashboard_latest CASCADE;
DROP VIEW IF EXISTS vw_active_alerts CASCADE;
DROP VIEW IF EXISTS vw_latest_classification CASCADE;

DROP TABLE IF EXISTS notification_logs CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS ai_process_logs CASCADE;
DROP TABLE IF EXISTS classifications CASCADE;
DROP TABLE IF EXISTS tb_emisi_alat_berat CASCADE;
DROP TABLE IF EXISTS tb_gas_tambang CASCADE;
DROP TABLE IF EXISTS tb_debu_tambang CASCADE;
DROP TABLE IF EXISTS sensor_readings CASCADE;
DROP TABLE IF EXISTS sensor_thresholds CASCADE;
DROP TABLE IF EXISTS calibration_profiles CASCADE;
DROP TABLE IF EXISTS device_sensors CASCADE;
DROP TABLE IF EXISTS sensor_parameters CASCADE;
DROP TABLE IF EXISTS sensor_definitions CASCADE;
DROP TABLE IF EXISTS device_logs CASCADE;
DROP TABLE IF EXISTS device_commands CASCADE;
DROP TABLE IF EXISTS device_states CASCADE;
DROP TABLE IF EXISTS device_configs CASCADE;
DROP TABLE IF EXISTS devices CASCADE;

-- Legacy tables from old schema
DROP TABLE IF EXISTS dht22_readings CASCADE;
DROP TABLE IF EXISTS sensors CASCADE;

-- ************************************************************
-- 0.5 EXTENSIONS
-- ************************************************************

CREATE EXTENSION IF NOT EXISTS "pgcrypto";      -- gen_random_uuid()

-- ************************************************************
-- 1. UTILITY FUNCTIONS
-- ************************************************************

-- ------------------------------------------------------------
-- fn_set_updated_at()
-- Trigger function to auto-set updated_at on every UPDATE.
-- Attached to all tables that carry an updated_at column.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ************************************************************
-- 2. DEVICE MANAGEMENT
-- ************************************************************


-- ============================================================
-- 2.1 devices
-- Registry of all ESP32 IoT devices deployed in the field.
-- UUID primary key so devices can be provisioned before first
-- connection and remain globally unique across sites.
-- ============================================================
CREATE TABLE devices (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    device_code     VARCHAR(50)     NOT NULL,
    device_name     VARCHAR(150)    NOT NULL,
    location        VARCHAR(200),
    latitude        NUMERIC(10, 7),
    longitude       NUMERIC(10, 7),
    firmware_ver    VARCHAR(50),
    description     TEXT,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_devices_code UNIQUE (device_code)
);

CREATE TRIGGER trg_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TABLE  devices IS 'Registry of ESP32 IoT devices deployed in mining sites.';
COMMENT ON COLUMN devices.id IS 'UUID primary key, auto-generated.';
COMMENT ON COLUMN devices.device_code IS 'Human-readable device identifier, e.g. ESP32-MINE-001.';
COMMENT ON COLUMN devices.device_name IS 'Descriptive name for display in dashboard.';
COMMENT ON COLUMN devices.location IS 'Textual description of deployment location.';
COMMENT ON COLUMN devices.latitude IS 'GPS latitude of device placement (WGS84).';
COMMENT ON COLUMN devices.longitude IS 'GPS longitude of device placement (WGS84).';
COMMENT ON COLUMN devices.firmware_ver IS 'Currently running firmware version string.';
COMMENT ON COLUMN devices.is_active IS 'Soft-delete flag. FALSE = device decommissioned.';

-- ============================================================
-- 2.2 device_configs
-- Key-value + JSONB configuration store per device.
-- Examples: reading_interval, sleep_mode, calibration_offset.
-- ============================================================
CREATE TABLE device_configs (
    id              BIGSERIAL       PRIMARY KEY,
    device_id       UUID            NOT NULL,
    config_key      VARCHAR(100)    NOT NULL,
    config_value    TEXT,
    config_json     JSONB,
    description     TEXT,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_device_configs_device
        FOREIGN KEY (device_id) REFERENCES devices (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT uq_device_configs_key
        UNIQUE (device_id, config_key)
);

CREATE TRIGGER trg_device_configs_updated_at
    BEFORE UPDATE ON device_configs
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TABLE  device_configs IS 'Key-value configuration store per device. Supports both text and JSONB values.';
COMMENT ON COLUMN device_configs.config_key IS 'Configuration parameter name, e.g. reading_interval_s.';
COMMENT ON COLUMN device_configs.config_value IS 'Scalar text value for the configuration parameter.';
COMMENT ON COLUMN device_configs.config_json IS 'Complex JSON value when a simple string is not sufficient.';

-- ============================================================
-- 2.3 device_states
-- Real-time operational state of each device.
-- One-to-one relationship with devices.
-- Updated by the device heartbeat / reading endpoint.
-- ============================================================
CREATE TABLE device_states (
    id              BIGSERIAL       PRIMARY KEY,
    device_id       UUID            NOT NULL,
    is_online       BOOLEAN         NOT NULL DEFAULT FALSE,
    power_state     VARCHAR(20)     NOT NULL DEFAULT 'off',
    battery_voltage NUMERIC(4, 2),
    wifi_rssi       INTEGER,
    uptime_seconds  BIGINT,
    last_seen_at    TIMESTAMPTZ,
    last_boot_at    TIMESTAMPTZ,
    last_command_at TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_device_states_device
        FOREIGN KEY (device_id) REFERENCES devices (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT uq_device_states_device
        UNIQUE (device_id),

    CONSTRAINT chk_device_states_power_state
        CHECK (power_state IN ('on', 'off', 'sleep', 'error'))
);

CREATE TRIGGER trg_device_states_updated_at
    BEFORE UPDATE ON device_states
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TABLE  device_states IS 'Real-time operational state per device. One row per device.';
COMMENT ON COLUMN device_states.is_online IS 'TRUE when the device has been seen within the heartbeat window.';
COMMENT ON COLUMN device_states.power_state IS 'Current power mode: on, off, sleep, or error.';
COMMENT ON COLUMN device_states.battery_voltage IS 'Last reported battery voltage in volts.';
COMMENT ON COLUMN device_states.wifi_rssi IS 'Last reported Wi-Fi signal strength in dBm.';
COMMENT ON COLUMN device_states.uptime_seconds IS 'Seconds since last boot as reported by the device.';

-- ============================================================
-- 2.4 device_commands
-- Command queue for sending instructions to devices.
-- Commands are created by the dashboard/API and polled or
-- pushed to the device on next connection.
-- ============================================================
CREATE TABLE device_commands (
    id              BIGSERIAL       PRIMARY KEY,
    device_id       UUID            NOT NULL,
    command         VARCHAR(50)     NOT NULL,
    payload         JSONB,
    status          VARCHAR(30)     NOT NULL DEFAULT 'pending',
    requested_by    VARCHAR(100),
    error_message   TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    executed_at     TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,

    CONSTRAINT fk_device_commands_device
        FOREIGN KEY (device_id) REFERENCES devices (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT chk_device_commands_command
        CHECK (command IN (
            'turn_on', 'turn_off', 'restart', 'sleep',
            'update_config', 'ota_update', 'calibrate',
            'factory_reset', 'diagnostic'
        )),

    CONSTRAINT chk_device_commands_status
        CHECK (status IN (
            'pending', 'sent', 'acknowledged',
            'executed', 'failed', 'expired'
        ))
);

COMMENT ON TABLE  device_commands IS 'Command queue for device remote control.';
COMMENT ON COLUMN device_commands.command IS 'The command verb to execute on the device.';
COMMENT ON COLUMN device_commands.payload IS 'Optional JSON payload with command parameters.';
COMMENT ON COLUMN device_commands.status IS 'Lifecycle status of the command.';
COMMENT ON COLUMN device_commands.expires_at IS 'Commands not executed by this time are marked expired.';

-- ============================================================
-- 2.5 device_logs
-- Chronological log of device events: boot, errors, OTA, etc.
-- ============================================================
CREATE TABLE device_logs (
    id              BIGSERIAL       PRIMARY KEY,
    device_id       UUID            NOT NULL,
    log_level       VARCHAR(20)     NOT NULL DEFAULT 'info',
    event_type      VARCHAR(50)     NOT NULL,
    message         TEXT,
    metadata        JSONB,
    recorded_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_device_logs_device
        FOREIGN KEY (device_id) REFERENCES devices (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT chk_device_logs_level
        CHECK (log_level IN (
            'debug', 'info', 'warning', 'error', 'critical'
        ))
);

COMMENT ON TABLE  device_logs IS 'Chronological event log per device (boot, errors, OTA updates, etc).';
COMMENT ON COLUMN device_logs.log_level IS 'Severity level: debug, info, warning, error, critical.';
COMMENT ON COLUMN device_logs.event_type IS 'Short event identifier, e.g. boot, ota_start, sensor_fault.';
COMMENT ON COLUMN device_logs.metadata IS 'Arbitrary JSON context for the event.';

-- ************************************************************
-- 3. SENSOR CATALOG (Extensible — no migration for new sensors)
-- ************************************************************

-- ============================================================
-- 3.1 sensor_definitions
-- Master catalog of sensor types. Adding a new sensor (e.g.
-- PMS5003) is just an INSERT — no schema migration needed.
-- ============================================================
CREATE TABLE sensor_definitions (
    id              BIGSERIAL       PRIMARY KEY,
    sensor_code     VARCHAR(50)     NOT NULL,
    sensor_name     VARCHAR(150)    NOT NULL,
    manufacturer    VARCHAR(100),
    description     TEXT,
    interface_type  VARCHAR(30),
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_sensor_definitions_code UNIQUE (sensor_code),

    CONSTRAINT chk_sensor_definitions_interface
        CHECK (interface_type IN (
            'analog', 'digital', 'i2c', 'spi', 'uart', 'onewire'
        ))
);

CREATE TRIGGER trg_sensor_definitions_updated_at
    BEFORE UPDATE ON sensor_definitions
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TABLE  sensor_definitions IS 'Master catalog of sensor types (DHT22, MQ4, PMS5003, etc). Extensible via INSERT.';
COMMENT ON COLUMN sensor_definitions.sensor_code IS 'Unique short code, e.g. DHT22, MQ4, PMS5003.';
COMMENT ON COLUMN sensor_definitions.interface_type IS 'Communication interface: analog, digital, i2c, spi, uart, onewire.';

-- ============================================================
-- 3.2 sensor_parameters
-- Each sensor can measure multiple parameters.
-- DHT22 → temperature, humidity
-- PMS5003 → pm25, pm10, pm1_0
-- Adding parameters = INSERT, not ALTER TABLE.
-- ============================================================
CREATE TABLE sensor_parameters (
    id              BIGSERIAL       PRIMARY KEY,
    sensor_def_id   BIGINT          NOT NULL,
    parameter_code  VARCHAR(50)     NOT NULL,
    parameter_name  VARCHAR(100)    NOT NULL,
    unit            VARCHAR(30),
    min_value       NUMERIC(12, 4),
    max_value       NUMERIC(12, 4),
    precision_dp    SMALLINT        NOT NULL DEFAULT 2,
    description     TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_sensor_parameters_def
        FOREIGN KEY (sensor_def_id) REFERENCES sensor_definitions (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT uq_sensor_parameters_code
        UNIQUE (sensor_def_id, parameter_code),

    CONSTRAINT chk_sensor_parameters_precision
        CHECK (precision_dp BETWEEN 0 AND 8),

    CONSTRAINT chk_sensor_parameters_range
        CHECK (min_value IS NULL OR max_value IS NULL OR min_value <= max_value)
);

COMMENT ON TABLE  sensor_parameters IS 'Parameters measured by each sensor type. E.g. DHT22 measures temperature and humidity.';
COMMENT ON COLUMN sensor_parameters.parameter_code IS 'Machine-readable code: temperature, humidity, pm25, ch4, etc.';
COMMENT ON COLUMN sensor_parameters.unit IS 'Measurement unit: °C, %, ppm, µg/m³, etc.';
COMMENT ON COLUMN sensor_parameters.min_value IS 'Physical minimum the sensor can measure.';
COMMENT ON COLUMN sensor_parameters.max_value IS 'Physical maximum the sensor can measure.';
COMMENT ON COLUMN sensor_parameters.precision_dp IS 'Number of decimal places for storage precision.';

-- ============================================================
-- 3.3 device_sensors
-- Junction table: which physical sensor is installed on which
-- device, at which GPIO pin / I2C address.
-- ============================================================
CREATE TABLE device_sensors (
    id              BIGSERIAL       PRIMARY KEY,
    device_id       UUID            NOT NULL,
    sensor_def_id   BIGINT          NOT NULL,
    gpio_pin        VARCHAR(20),
    i2c_address     VARCHAR(10),
    install_date    DATE,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    notes           TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_device_sensors_device
        FOREIGN KEY (device_id) REFERENCES devices (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_device_sensors_def
        FOREIGN KEY (sensor_def_id) REFERENCES sensor_definitions (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT uq_device_sensors_mapping
        UNIQUE (device_id, sensor_def_id)
);

CREATE TRIGGER trg_device_sensors_updated_at
    BEFORE UPDATE ON device_sensors
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TABLE  device_sensors IS 'Maps which sensors are physically installed on each device.';
COMMENT ON COLUMN device_sensors.gpio_pin IS 'GPIO pin assignment on the ESP32, e.g. GPIO4, GPIO34.';
COMMENT ON COLUMN device_sensors.i2c_address IS 'I2C address if applicable, e.g. 0x68 for DS3231 RTC.';
COMMENT ON COLUMN device_sensors.install_date IS 'Date the sensor was physically installed.';

-- ============================================================
-- 3.4 calibration_profiles
-- Calibration data per sensor definition. MQ-series sensors
-- need R0, slope, and offset values for accurate readings.
-- ============================================================
CREATE TABLE calibration_profiles (
    id              BIGSERIAL       PRIMARY KEY,
    sensor_def_id   BIGINT          NOT NULL,
    profile_name    VARCHAR(100)    NOT NULL,
    r0              NUMERIC(12, 6),
    slope           NUMERIC(12, 6),
    "offset"        NUMERIC(12, 6),
    calibrated_at   TIMESTAMPTZ,
    calibrated_by   VARCHAR(100),
    notes           TEXT,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_calibration_profiles_def
        FOREIGN KEY (sensor_def_id) REFERENCES sensor_definitions (id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TRIGGER trg_calibration_profiles_updated_at
    BEFORE UPDATE ON calibration_profiles
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TABLE  calibration_profiles IS 'Calibration profiles for MQ-series and other analog sensors.';
COMMENT ON COLUMN calibration_profiles.r0 IS 'Baseline resistance in clean air (MQ sensors).';
COMMENT ON COLUMN calibration_profiles.slope IS 'Calibration curve slope factor.';
COMMENT ON COLUMN calibration_profiles."offset" IS 'Calibration curve offset value.';

-- ============================================================
-- 3.5 sensor_thresholds
-- Warning and danger thresholds per parameter.
-- Used by AI/Fuzzy engine to classify risk levels.
-- NEVER hardcode thresholds in backend code — read from here.
-- ============================================================
CREATE TABLE sensor_thresholds (
    id              BIGSERIAL       PRIMARY KEY,
    parameter_code  VARCHAR(50)     NOT NULL,
    parameter_name  VARCHAR(100),
    unit            VARCHAR(30),
    warning_min     NUMERIC(12, 4),
    warning_max     NUMERIC(12, 4),
    danger_min      NUMERIC(12, 4),
    danger_max      NUMERIC(12, 4),
    critical_min    NUMERIC(12, 4),
    critical_max    NUMERIC(12, 4),
    source          VARCHAR(100),
    notes           TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_sensor_thresholds_param UNIQUE (parameter_code)
);

CREATE TRIGGER trg_sensor_thresholds_updated_at
    BEFORE UPDATE ON sensor_thresholds
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TABLE  sensor_thresholds IS 'Warning/danger/critical thresholds per parameter. Used by AI/Fuzzy for classification.';
COMMENT ON COLUMN sensor_thresholds.parameter_code IS 'References the parameter_code from sensor_parameters.';
COMMENT ON COLUMN sensor_thresholds.warning_min IS 'Lower bound of warning range.';
COMMENT ON COLUMN sensor_thresholds.warning_max IS 'Upper bound of warning range.';
COMMENT ON COLUMN sensor_thresholds.danger_min IS 'Lower bound of danger range.';
COMMENT ON COLUMN sensor_thresholds.danger_max IS 'Upper bound of danger range.';
COMMENT ON COLUMN sensor_thresholds.critical_min IS 'Lower bound of critical range.';
COMMENT ON COLUMN sensor_thresholds.critical_max IS 'Upper bound of critical range.';
COMMENT ON COLUMN sensor_thresholds.source IS 'Regulatory source, e.g. PP 22/2021, WHO AQG, NIOSH.';

-- ************************************************************
-- 4. READING DATA (Header-Detail Pattern)
-- ************************************************************
-- ESP32 sends ONE payload → ONE sensor_readings row (header)
-- Backend splits data → tb_debu / tb_gas / tb_emisi (details)
-- All detail tables share the same reading_id FK.

-- ============================================================
-- 4.1 sensor_readings (HEADER)
-- One row per ESP32 payload. Contains common ambient data
-- (temperature, humidity from DHT22) and device telemetry
-- (battery, wifi, rtc sync status).
-- ============================================================
CREATE TABLE sensor_readings (
    id              BIGSERIAL       PRIMARY KEY,
    device_id       UUID            NOT NULL,
    recorded_at     TIMESTAMPTZ     NOT NULL,
    temperature     NUMERIC(6, 2),
    humidity        NUMERIC(6, 2),
    battery_voltage NUMERIC(4, 2),
    wifi_rssi       INTEGER,
    rtc_synced      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_sensor_readings_device
        FOREIGN KEY (device_id) REFERENCES devices (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT chk_sensor_readings_temperature
        CHECK (temperature IS NULL OR temperature BETWEEN -40 AND 85),

    CONSTRAINT chk_sensor_readings_humidity
        CHECK (humidity IS NULL OR humidity BETWEEN 0 AND 100)
);

COMMENT ON TABLE  sensor_readings IS 'Header table: one row per ESP32 reading payload. Core of the header-detail pattern.';
COMMENT ON COLUMN sensor_readings.device_id IS 'The device that produced this reading.';
COMMENT ON COLUMN sensor_readings.recorded_at IS 'Timestamp from the device RTC (or server time if RTC not synced).';
COMMENT ON COLUMN sensor_readings.temperature IS 'Ambient temperature from DHT22 in °C.';
COMMENT ON COLUMN sensor_readings.humidity IS 'Relative humidity from DHT22 in %.';
COMMENT ON COLUMN sensor_readings.battery_voltage IS 'Battery voltage at time of reading in volts.';
COMMENT ON COLUMN sensor_readings.wifi_rssi IS 'Wi-Fi signal strength at time of reading in dBm.';
COMMENT ON COLUMN sensor_readings.rtc_synced IS 'TRUE if the device RTC was NTP-synced at the time of reading.';

-- ============================================================
-- 4.2 tb_debu_tambang (DETAIL — Dust / Particulate Matter)
-- PM2.5 and PM10 readings from PMS5003 or equivalent.
-- One-to-one with sensor_readings via reading_id.
-- Currently NULL if PMS5003 not yet installed.
-- ============================================================
CREATE TABLE tb_debu_tambang (
    id              BIGSERIAL       PRIMARY KEY,
    reading_id      BIGINT          NOT NULL,
    pm25            NUMERIC(10, 2),
    pm10            NUMERIC(10, 2),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_debu_tambang_reading
        FOREIGN KEY (reading_id) REFERENCES sensor_readings (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT uq_debu_tambang_reading
        UNIQUE (reading_id),

    CONSTRAINT chk_debu_tambang_pm25
        CHECK (pm25 IS NULL OR pm25 >= 0),

    CONSTRAINT chk_debu_tambang_pm10
        CHECK (pm10 IS NULL OR pm10 >= 0)
);

COMMENT ON TABLE  tb_debu_tambang IS 'Detail table: dust/particulate matter readings per sensor_readings row.';
COMMENT ON COLUMN tb_debu_tambang.reading_id IS 'FK to sensor_readings. One-to-one relationship.';
COMMENT ON COLUMN tb_debu_tambang.pm25 IS 'PM2.5 concentration in µg/m³.';
COMMENT ON COLUMN tb_debu_tambang.pm10 IS 'PM10 concentration in µg/m³.';

-- ============================================================
-- 4.3 tb_gas_tambang (DETAIL — Mine Gas)
-- CH4 (methane) from MQ4 and H2S from MQ136.
-- ============================================================
CREATE TABLE tb_gas_tambang (
    id              BIGSERIAL       PRIMARY KEY,
    reading_id      BIGINT          NOT NULL,
    ch4             NUMERIC(10, 4),
    h2s             NUMERIC(10, 4),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_gas_tambang_reading
        FOREIGN KEY (reading_id) REFERENCES sensor_readings (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT uq_gas_tambang_reading
        UNIQUE (reading_id),

    CONSTRAINT chk_gas_tambang_ch4
        CHECK (ch4 IS NULL OR ch4 >= 0),

    CONSTRAINT chk_gas_tambang_h2s
        CHECK (h2s IS NULL OR h2s >= 0)
);

COMMENT ON TABLE  tb_gas_tambang IS 'Detail table: mine gas readings (CH4, H2S) per sensor_readings row.';
COMMENT ON COLUMN tb_gas_tambang.reading_id IS 'FK to sensor_readings. One-to-one relationship.';
COMMENT ON COLUMN tb_gas_tambang.ch4 IS 'Methane concentration in ppm (MQ4 sensor).';
COMMENT ON COLUMN tb_gas_tambang.h2s IS 'Hydrogen sulfide concentration in ppm (MQ136 sensor, future).';

-- ============================================================
-- 4.4 tb_emisi_alat_berat (DETAIL — Heavy Equipment Emission)
-- CO from MQ7 and CO2 estimated from MQ135.
-- ============================================================
CREATE TABLE tb_emisi_alat_berat (
    id              BIGSERIAL       PRIMARY KEY,
    reading_id      BIGINT          NOT NULL,
    co              NUMERIC(10, 4),
    co2_estimated   NUMERIC(10, 4),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_emisi_alat_berat_reading
        FOREIGN KEY (reading_id) REFERENCES sensor_readings (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT uq_emisi_alat_berat_reading
        UNIQUE (reading_id),

    CONSTRAINT chk_emisi_alat_berat_co
        CHECK (co IS NULL OR co >= 0),

    CONSTRAINT chk_emisi_alat_berat_co2
        CHECK (co2_estimated IS NULL OR co2_estimated >= 0)
);

COMMENT ON TABLE  tb_emisi_alat_berat IS 'Detail table: heavy equipment emission readings (CO, CO2) per sensor_readings row.';
COMMENT ON COLUMN tb_emisi_alat_berat.reading_id IS 'FK to sensor_readings. One-to-one relationship.';
COMMENT ON COLUMN tb_emisi_alat_berat.co IS 'Carbon monoxide concentration in ppm (MQ7 sensor).';
COMMENT ON COLUMN tb_emisi_alat_berat.co2_estimated IS 'Estimated CO2 concentration in ppm (MQ135 sensor).';

-- ************************************************************
-- 5. AI & CLASSIFICATION
-- ************************************************************

-- ============================================================
-- 5.1 classifications
-- AI/Fuzzy classification result per reading per category.
-- Each reading can have up to 3 classifications (one per
-- category: debu_tambang, gas_tambang, emisi_alat_berat).
-- ============================================================
CREATE TABLE classifications (
    id              BIGSERIAL       PRIMARY KEY,
    reading_id      BIGINT          NOT NULL,
    category        VARCHAR(50)     NOT NULL,
    classification  VARCHAR(100)    NOT NULL,
    risk_level      VARCHAR(30)     NOT NULL,
    confidence      NUMERIC(5, 4),
    score           NUMERIC(10, 4),
    message         TEXT,
    model_name      VARCHAR(100),
    model_version   VARCHAR(50),
    processed_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_classifications_reading
        FOREIGN KEY (reading_id) REFERENCES sensor_readings (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT uq_classifications_reading_category
        UNIQUE (reading_id, category),

    CONSTRAINT chk_classifications_category
        CHECK (category IN (
            'debu_tambang', 'gas_tambang', 'emisi_alat_berat'
        )),

    CONSTRAINT chk_classifications_risk_level
        CHECK (risk_level IN (
            'aman', 'perhatian', 'warning', 'danger', 'critical'
        )),

    CONSTRAINT chk_classifications_confidence
        CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1)
);

COMMENT ON TABLE  classifications IS 'AI/Fuzzy classification results. One row per reading per category.';
COMMENT ON COLUMN classifications.reading_id IS 'FK to sensor_readings being classified.';
COMMENT ON COLUMN classifications.category IS 'Which detail table this classification is for.';
COMMENT ON COLUMN classifications.classification IS 'Human-readable classification label, e.g. Bahaya Tinggi.';
COMMENT ON COLUMN classifications.risk_level IS 'Risk level: aman, perhatian, warning, danger, critical.';
COMMENT ON COLUMN classifications.confidence IS 'Model confidence score between 0.0 and 1.0.';
COMMENT ON COLUMN classifications.score IS 'Numeric risk score from the fuzzy/AI engine.';
COMMENT ON COLUMN classifications.model_name IS 'Name of the AI model or fuzzy engine that produced this result.';
COMMENT ON COLUMN classifications.model_version IS 'Version of the model, e.g. v1.2.0.';

-- ============================================================
-- 5.2 ai_process_logs
-- Telemetry for each AI/Fuzzy processing run.
-- Tracks duration, success/failure, and optional I/O snapshots
-- for debugging and performance monitoring.
-- ============================================================
CREATE TABLE ai_process_logs (
    id              BIGSERIAL       PRIMARY KEY,
    reading_id      BIGINT          NOT NULL,
    model_name      VARCHAR(100)    NOT NULL,
    model_version   VARCHAR(50),
    duration_ms     INTEGER,
    status          VARCHAR(30)     NOT NULL DEFAULT 'success',
    error_message   TEXT,
    input_snapshot  JSONB,
    output_snapshot JSONB,
    processed_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ai_process_logs_reading
        FOREIGN KEY (reading_id) REFERENCES sensor_readings (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT chk_ai_process_logs_status
        CHECK (status IN ('success', 'failed', 'timeout', 'skipped')),

    CONSTRAINT chk_ai_process_logs_duration
        CHECK (duration_ms IS NULL OR duration_ms >= 0)
);

COMMENT ON TABLE  ai_process_logs IS 'Telemetry log for AI/Fuzzy processing runs.';
COMMENT ON COLUMN ai_process_logs.duration_ms IS 'Processing time in milliseconds.';
COMMENT ON COLUMN ai_process_logs.status IS 'Outcome: success, failed, timeout, or skipped.';
COMMENT ON COLUMN ai_process_logs.input_snapshot IS 'JSON snapshot of the input data sent to the model.';
COMMENT ON COLUMN ai_process_logs.output_snapshot IS 'JSON snapshot of the raw model output.';

-- ************************************************************
-- 6. ALERTING & NOTIFICATION
-- ************************************************************

-- ============================================================
-- 6.1 alerts
-- Generated when a classification exceeds thresholds.
-- Lifecycle: open → acknowledged → resolved (or escalated/expired).
-- ============================================================
CREATE TABLE alerts (
    id                BIGSERIAL     PRIMARY KEY,
    classification_id BIGINT        NOT NULL,
    device_id         UUID          NOT NULL,
    alert_type        VARCHAR(50)   NOT NULL DEFAULT 'threshold',
    severity          VARCHAR(30),
    status            VARCHAR(30)   NOT NULL DEFAULT 'open',
    message           TEXT,
    acknowledged_at   TIMESTAMPTZ,
    acknowledged_by   VARCHAR(100),
    resolved_at       TIMESTAMPTZ,
    resolved_by       VARCHAR(100),
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_alerts_classification
        FOREIGN KEY (classification_id) REFERENCES classifications (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_alerts_device
        FOREIGN KEY (device_id) REFERENCES devices (id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT chk_alerts_severity
        CHECK (severity IS NULL OR severity IN (
            'low', 'medium', 'high', 'critical'
        )),

    CONSTRAINT chk_alerts_status
        CHECK (status IN (
            'open', 'acknowledged', 'resolved',
            'escalated', 'expired'
        ))
);

CREATE TRIGGER trg_alerts_updated_at
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TABLE  alerts IS 'Alert records triggered by dangerous classifications.';
COMMENT ON COLUMN alerts.classification_id IS 'The classification that triggered this alert.';
COMMENT ON COLUMN alerts.device_id IS 'The device associated with this alert.';
COMMENT ON COLUMN alerts.alert_type IS 'Type of alert: threshold, anomaly, system, etc.';
COMMENT ON COLUMN alerts.severity IS 'Alert severity: low, medium, high, critical.';
COMMENT ON COLUMN alerts.status IS 'Alert lifecycle: open → acknowledged → resolved/escalated/expired.';

-- ============================================================
-- 6.2 notification_logs
-- Record of every notification attempt (email, SMS, push,
-- Telegram, WhatsApp, webhook).
-- ============================================================
CREATE TABLE notification_logs (
    id              BIGSERIAL       PRIMARY KEY,
    alert_id        BIGINT,
    channel         VARCHAR(30)     NOT NULL,
    recipient       VARCHAR(200)    NOT NULL,
    subject         VARCHAR(300),
    body            TEXT,
    status          VARCHAR(30)     NOT NULL DEFAULT 'pending',
    response        TEXT,
    retry_count     SMALLINT        NOT NULL DEFAULT 0,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_notification_logs_alert
        FOREIGN KEY (alert_id) REFERENCES alerts (id)
        ON UPDATE CASCADE ON DELETE SET NULL,

    CONSTRAINT chk_notification_logs_channel
        CHECK (channel IN (
            'email', 'sms', 'push', 'webhook',
            'telegram', 'whatsapp'
        )),

    CONSTRAINT chk_notification_logs_status
        CHECK (status IN (
            'pending', 'sent', 'delivered',
            'failed', 'bounced'
        )),

    CONSTRAINT chk_notification_logs_retry
        CHECK (retry_count >= 0)
);

COMMENT ON TABLE  notification_logs IS 'Audit log of every notification attempt across all channels.';
COMMENT ON COLUMN notification_logs.channel IS 'Delivery channel: email, sms, push, webhook, telegram, whatsapp.';
COMMENT ON COLUMN notification_logs.recipient IS 'Target address/number/ID for the notification.';
COMMENT ON COLUMN notification_logs.status IS 'Delivery status: pending, sent, delivered, failed, bounced.';
COMMENT ON COLUMN notification_logs.retry_count IS 'Number of retry attempts made.';

-- ************************************************************
-- 7. INDEXES
-- ************************************************************
-- Naming convention: idx_{table}_{columns}

-- devices
CREATE INDEX idx_devices_active
    ON devices (is_active);

CREATE INDEX idx_devices_location
    ON devices (latitude, longitude)
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- device_configs
CREATE INDEX idx_device_configs_device
    ON device_configs (device_id);

-- device_states
CREATE INDEX idx_device_states_online
    ON device_states (is_online);

CREATE INDEX idx_device_states_last_seen
    ON device_states (last_seen_at DESC);

-- device_commands
CREATE INDEX idx_device_commands_device_status
    ON device_commands (device_id, status);

CREATE INDEX idx_device_commands_created
    ON device_commands (created_at DESC);

CREATE INDEX idx_device_commands_pending
    ON device_commands (device_id, created_at DESC)
    WHERE status = 'pending';

-- device_logs
CREATE INDEX idx_device_logs_device_time
    ON device_logs (device_id, recorded_at DESC);

CREATE INDEX idx_device_logs_level
    ON device_logs (log_level)
    WHERE log_level IN ('error', 'critical');

-- sensor_definitions
CREATE INDEX idx_sensor_definitions_active
    ON sensor_definitions (is_active);

-- sensor_parameters
CREATE INDEX idx_sensor_parameters_def
    ON sensor_parameters (sensor_def_id);

CREATE INDEX idx_sensor_parameters_code
    ON sensor_parameters (parameter_code);

-- device_sensors
CREATE INDEX idx_device_sensors_device
    ON device_sensors (device_id);

CREATE INDEX idx_device_sensors_def
    ON device_sensors (sensor_def_id);

-- calibration_profiles
CREATE INDEX idx_calibration_profiles_def
    ON calibration_profiles (sensor_def_id);

CREATE INDEX idx_calibration_profiles_active
    ON calibration_profiles (sensor_def_id, is_active)
    WHERE is_active = TRUE;

-- sensor_readings (CRITICAL for dashboard performance)
CREATE INDEX idx_sensor_readings_device_time
    ON sensor_readings (device_id, recorded_at DESC);

CREATE INDEX idx_sensor_readings_time
    ON sensor_readings (recorded_at DESC);

-- tb_debu_tambang
-- reading_id already has a UNIQUE constraint → implicit index

-- tb_gas_tambang
-- reading_id already has a UNIQUE constraint → implicit index

-- tb_emisi_alat_berat
-- reading_id already has a UNIQUE constraint → implicit index

-- classifications
CREATE INDEX idx_classifications_reading
    ON classifications (reading_id);

CREATE INDEX idx_classifications_category
    ON classifications (category);

CREATE INDEX idx_classifications_risk_level
    ON classifications (risk_level);

CREATE INDEX idx_classifications_processed
    ON classifications (processed_at DESC);

-- ai_process_logs
CREATE INDEX idx_ai_process_logs_reading
    ON ai_process_logs (reading_id);

CREATE INDEX idx_ai_process_logs_status
    ON ai_process_logs (status)
    WHERE status != 'success';

-- alerts
CREATE INDEX idx_alerts_status
    ON alerts (status);

CREATE INDEX idx_alerts_device_status
    ON alerts (device_id, status);

CREATE INDEX idx_alerts_classification
    ON alerts (classification_id);

CREATE INDEX idx_alerts_created
    ON alerts (created_at DESC);

CREATE INDEX idx_alerts_active
    ON alerts (device_id, created_at DESC)
    WHERE status IN ('open', 'acknowledged');

-- notification_logs
CREATE INDEX idx_notification_logs_alert
    ON notification_logs (alert_id);

CREATE INDEX idx_notification_logs_status
    ON notification_logs (status);

CREATE INDEX idx_notification_logs_channel
    ON notification_logs (channel, status);

CREATE INDEX idx_notification_logs_sent
    ON notification_logs (sent_at DESC)
    WHERE sent_at IS NOT NULL;

-- sensor_thresholds
-- parameter_code already has a UNIQUE constraint → implicit index

-- ************************************************************
-- 8. VIEWS
-- ************************************************************

-- ============================================================
-- 8.1 vw_dashboard_latest
-- Latest reading per device with all detail tables joined.
-- Powers the real-time dashboard overview.
-- ============================================================
CREATE OR REPLACE VIEW vw_dashboard_latest AS
SELECT
    d.id                AS device_id,
    d.device_code,
    d.device_name,
    d.location,
    d.latitude,
    d.longitude,
    ds.is_online,
    ds.power_state,
    ds.battery_voltage  AS state_battery,
    ds.wifi_rssi        AS state_wifi_rssi,
    ds.last_seen_at,
    sr.id               AS reading_id,
    sr.recorded_at,
    sr.temperature,
    sr.humidity,
    sr.battery_voltage  AS reading_battery,
    sr.wifi_rssi        AS reading_wifi_rssi,
    sr.rtc_synced,
    debu.pm25,
    debu.pm10,
    gas.ch4,
    gas.h2s,
    emisi.co,
    emisi.co2_estimated
FROM devices d
LEFT JOIN device_states ds ON ds.device_id = d.id
LEFT JOIN LATERAL (
    SELECT *
    FROM sensor_readings
    WHERE device_id = d.id
    ORDER BY recorded_at DESC
    LIMIT 1
) sr ON TRUE
LEFT JOIN tb_debu_tambang    debu  ON debu.reading_id  = sr.id
LEFT JOIN tb_gas_tambang     gas   ON gas.reading_id   = sr.id
LEFT JOIN tb_emisi_alat_berat emisi ON emisi.reading_id = sr.id
WHERE d.is_active = TRUE;

COMMENT ON VIEW vw_dashboard_latest IS 'Latest reading per active device with all sensor details. Powers the real-time dashboard.';

-- ============================================================
-- 8.2 vw_active_alerts
-- Currently open or acknowledged alerts with device and
-- classification context.
-- ============================================================
CREATE OR REPLACE VIEW vw_active_alerts AS
SELECT
    a.id                AS alert_id,
    a.alert_type,
    a.severity,
    a.status            AS alert_status,
    a.message           AS alert_message,
    a.created_at        AS alert_created_at,
    a.acknowledged_at,
    a.acknowledged_by,
    d.id                AS device_id,
    d.device_code,
    d.device_name,
    d.location,
    c.id                AS classification_id,
    c.category,
    c.classification,
    c.risk_level,
    c.score,
    c.model_name,
    sr.recorded_at      AS reading_recorded_at
FROM alerts a
JOIN classifications c ON c.id = a.classification_id
JOIN sensor_readings sr ON sr.id = c.reading_id
JOIN devices d ON d.id = a.device_id
WHERE a.status IN ('open', 'acknowledged')
ORDER BY
    CASE a.severity
        WHEN 'critical' THEN 1
        WHEN 'high'     THEN 2
        WHEN 'medium'   THEN 3
        WHEN 'low'      THEN 4
        ELSE 5
    END,
    a.created_at DESC;

COMMENT ON VIEW vw_active_alerts IS 'Active (open/acknowledged) alerts ordered by severity, with device and classification details.';

-- ============================================================
-- 8.3 vw_latest_classification
-- Most recent classification per device per category.
-- Uses DISTINCT ON for efficient deduplication.
-- ============================================================
CREATE OR REPLACE VIEW vw_latest_classification AS
SELECT DISTINCT ON (sr.device_id, c.category)
    sr.device_id,
    d.device_code,
    d.device_name,
    c.id                AS classification_id,
    c.reading_id,
    c.category,
    c.classification,
    c.risk_level,
    c.confidence,
    c.score,
    c.message,
    c.model_name,
    c.model_version,
    c.processed_at,
    sr.recorded_at      AS reading_recorded_at
FROM classifications c
JOIN sensor_readings sr ON sr.id = c.reading_id
JOIN devices d ON d.id = sr.device_id
ORDER BY sr.device_id, c.category, c.processed_at DESC;

COMMENT ON VIEW vw_latest_classification IS 'Most recent classification per device per category (debu, gas, emisi).';

-- ************************************************************
-- 9. MASTER CATALOG SEED DATA
-- ************************************************************
-- Baseline configuration catalog. No device/reading transaction data.

DO $$
DECLARE
    v_dht22_id  BIGINT;
    v_mq4_id    BIGINT;
    v_mq7_id    BIGINT;
    v_mq135_id  BIGINT;
    v_rtc_id    BIGINT;
BEGIN

    -- 9.1 Sensor Definitions
    INSERT INTO sensor_definitions (sensor_code, sensor_name, manufacturer, description, interface_type)
    VALUES ('DHT22', 'DHT22 Temperature & Humidity Sensor', 'Aosong Electronics', 'Digital temperature and humidity sensor.', 'digital')
    ON CONFLICT (sensor_code) DO UPDATE SET
        sensor_name    = EXCLUDED.sensor_name,
        manufacturer   = EXCLUDED.manufacturer,
        description    = EXCLUDED.description,
        interface_type = EXCLUDED.interface_type,
        updated_at     = NOW()
    RETURNING id INTO v_dht22_id;

    INSERT INTO sensor_definitions (sensor_code, sensor_name, manufacturer, description, interface_type)
    VALUES ('MQ4', 'MQ-4 Methane Gas Sensor', 'Winsen Electronics', 'Semiconductor gas sensor for methane (CH4). Range: 300–10000 ppm.', 'analog')
    ON CONFLICT (sensor_code) DO UPDATE SET
        sensor_name    = EXCLUDED.sensor_name,
        manufacturer   = EXCLUDED.manufacturer,
        description    = EXCLUDED.description,
        interface_type = EXCLUDED.interface_type,
        updated_at     = NOW()
    RETURNING id INTO v_mq4_id;

    INSERT INTO sensor_definitions (sensor_code, sensor_name, manufacturer, description, interface_type)
    VALUES ('MQ7', 'MQ-7 Carbon Monoxide Sensor', 'Winsen Electronics', 'Semiconductor gas sensor for carbon monoxide (CO). Range: 20–2000 ppm.', 'analog')
    ON CONFLICT (sensor_code) DO UPDATE SET
        sensor_name    = EXCLUDED.sensor_name,
        manufacturer   = EXCLUDED.manufacturer,
        description    = EXCLUDED.description,
        interface_type = EXCLUDED.interface_type,
        updated_at     = NOW()
    RETURNING id INTO v_mq7_id;

    INSERT INTO sensor_definitions (sensor_code, sensor_name, manufacturer, description, interface_type)
    VALUES ('MQ135', 'MQ-135 Air Quality Sensor', 'Winsen Electronics', 'Semiconductor gas sensor for CO2 estimation.', 'analog')
    ON CONFLICT (sensor_code) DO UPDATE SET
        sensor_name    = EXCLUDED.sensor_name,
        manufacturer   = EXCLUDED.manufacturer,
        description    = EXCLUDED.description,
        interface_type = EXCLUDED.interface_type,
        updated_at     = NOW()
    RETURNING id INTO v_mq135_id;

    INSERT INTO sensor_definitions (sensor_code, sensor_name, manufacturer, description, interface_type)
    VALUES ('DS3231', 'DS3231 Real-Time Clock', 'Maxim Integrated', 'High-precision I2C real-time clock.', 'i2c')
    ON CONFLICT (sensor_code) DO UPDATE SET
        sensor_name    = EXCLUDED.sensor_name,
        manufacturer   = EXCLUDED.manufacturer,
        description    = EXCLUDED.description,
        interface_type = EXCLUDED.interface_type,
        updated_at     = NOW()
    RETURNING id INTO v_rtc_id;

    -- 9.2 Sensor Parameters
    -- DHT22 parameters
    INSERT INTO sensor_parameters (sensor_def_id, parameter_code, parameter_name, unit, min_value, max_value, precision_dp, description)
    VALUES (v_dht22_id, 'temperature', 'Temperature', '°C', -40.0000, 80.0000, 2, 'Ambient temperature.')
    ON CONFLICT (sensor_def_id, parameter_code) DO NOTHING;

    INSERT INTO sensor_parameters (sensor_def_id, parameter_code, parameter_name, unit, min_value, max_value, precision_dp, description)
    VALUES (v_dht22_id, 'humidity', 'Relative Humidity', '%', 0.0000, 100.0000, 2, 'Relative humidity.')
    ON CONFLICT (sensor_def_id, parameter_code) DO NOTHING;

    -- MQ4 parameters
    INSERT INTO sensor_parameters (sensor_def_id, parameter_code, parameter_name, unit, min_value, max_value, precision_dp, description)
    VALUES (v_mq4_id, 'ch4', 'Methane (CH₄)', 'ppm', 300.0000, 10000.0000, 4, 'Methane gas concentration.')
    ON CONFLICT (sensor_def_id, parameter_code) DO NOTHING;

    -- MQ7 parameters
    INSERT INTO sensor_parameters (sensor_def_id, parameter_code, parameter_name, unit, min_value, max_value, precision_dp, description)
    VALUES (v_mq7_id, 'co', 'Carbon Monoxide (CO)', 'ppm', 20.0000, 2000.0000, 4, 'Carbon monoxide concentration.')
    ON CONFLICT (sensor_def_id, parameter_code) DO NOTHING;

    -- MQ135 parameters
    INSERT INTO sensor_parameters (sensor_def_id, parameter_code, parameter_name, unit, min_value, max_value, precision_dp, description)
    VALUES (v_mq135_id, 'co2_estimated', 'Estimated CO₂', 'ppm', 400.0000, 5000.0000, 4, 'Estimated CO2 concentration.')
    ON CONFLICT (sensor_def_id, parameter_code) DO NOTHING;

    -- DS3231 parameters
    INSERT INTO sensor_parameters (sensor_def_id, parameter_code, parameter_name, unit, min_value, max_value, precision_dp, description)
    VALUES (v_rtc_id, 'rtc_datetime', 'RTC Date/Time', 'datetime', NULL, NULL, 0, 'Real-time clock timestamp.')
    ON CONFLICT (sensor_def_id, parameter_code) DO NOTHING;

    -- 9.3 Calibration Profile
    INSERT INTO calibration_profiles (sensor_def_id, profile_name, r0, slope, "offset", calibrated_by, notes)
    VALUES (
        v_mq135_id,
        'MQ135 Factory Baseline',
        76.630000,
        -0.420000,
        1.200000,
        'Factory',
        'Default factory calibration values for MQ135.'
    ) ON CONFLICT DO NOTHING;

END $$;

-- 9.4 Sensor Thresholds (Required for Fuzzy classification limits)
INSERT INTO sensor_thresholds (parameter_code, parameter_name, unit, warning_min, warning_max, danger_min, danger_max, critical_min, critical_max, source, notes)
VALUES
    (
        'pm25', 'PM2.5 (Fine Particulate)', 'µg/m³',
        35.0000, 75.0000,
        75.0001, 150.0000,
        150.0001, 500.0000,
        'PP 22/2021 & WHO AQG 2021',
        'PM2.5 thresholds aligned with Indonesian standards.'
    ),
    (
        'pm10', 'PM10 (Coarse Particulate)', 'µg/m³',
        50.0000, 150.0000,
        150.0001, 350.0000,
        350.0001, 600.0000,
        'PP 22/2021',
        'PM10 thresholds for mining dust monitoring.'
    ),
    (
        'ch4', 'Methane (CH₄)', 'ppm',
        1000.0000, 5000.0000,
        5000.0001, 10000.0000,
        10000.0001, 50000.0000,
        'NIOSH REL',
        'CH4 explosive range starts at 5% (50000 ppm).'
    ),
    (
        'h2s', 'Hydrogen Sulfide (H₂S)', 'ppm',
        5.0000, 10.0000,
        10.0001, 20.0000,
        20.0001, 100.0000,
        'NIOSH REL',
        'H2S IDLH = 50 ppm.'
    ),
    (
        'co', 'Carbon Monoxide (CO)', 'ppm',
        9.0000, 35.0000,
        35.0001, 200.0000,
        200.0001, 1200.0000,
        'NIOSH REL',
        'CO IDLH = 1200 ppm.'
    ),
    (
        'co2_estimated', 'Estimated CO₂', 'ppm',
        1000.0000, 2000.0000,
        2000.0001, 5000.0000,
        5000.0001, 40000.0000,
        'ASHRAE & NIOSH',
        'CO2 TWA = 5000 ppm.'
    )
ON CONFLICT (parameter_code) DO UPDATE SET
    parameter_name = EXCLUDED.parameter_name,
    unit           = EXCLUDED.unit,
    warning_min    = EXCLUDED.warning_min,
    warning_max    = EXCLUDED.warning_max,
    danger_min     = EXCLUDED.danger_min,
    danger_max     = EXCLUDED.danger_max,
    critical_min   = EXCLUDED.critical_min,
    critical_max   = EXCLUDED.critical_max,
    source         = EXCLUDED.source,
    notes          = EXCLUDED.notes,
    updated_at     = NOW();



-- ************************************************************
-- 10. FINAL VERIFICATION NOTICE
-- ************************************************************

DO $$
DECLARE
    v_table_count  INTEGER;
    v_view_count   INTEGER;
    v_index_count  INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_type = 'BASE TABLE';

    SELECT COUNT(*) INTO v_view_count
    FROM information_schema.views
    WHERE table_schema = 'public';

    SELECT COUNT(*) INTO v_index_count
    FROM pg_indexes
    WHERE schemaname = 'public';

    RAISE NOTICE '============================================================';
    RAISE NOTICE 'SIMOSI Schema v2.0 — Installation Complete';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Tables created : %', v_table_count;
    RAISE NOTICE 'Views created  : %', v_view_count;
    RAISE NOTICE 'Indexes created: %', v_index_count;
    RAISE NOTICE '============================================================';
END $$;

-- ************************************************************
-- END OF SCHEMA
-- ************************************************************
