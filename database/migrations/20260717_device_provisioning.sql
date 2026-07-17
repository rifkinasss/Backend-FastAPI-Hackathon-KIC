-- Apply once to existing SIMOSI PostgreSQL databases.
ALTER TABLE devices ADD COLUMN IF NOT EXISTS hardware_id VARCHAR(64);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS provisioning_status VARCHAR(20) NOT NULL DEFAULT 'approved';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_devices_hardware_id'
    ) THEN
        ALTER TABLE devices ADD CONSTRAINT uq_devices_hardware_id UNIQUE (hardware_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_devices_provisioning_status'
    ) THEN
        ALTER TABLE devices ADD CONSTRAINT chk_devices_provisioning_status
            CHECK (provisioning_status IN ('pending', 'approved', 'rejected'));
    END IF;
END $$;
