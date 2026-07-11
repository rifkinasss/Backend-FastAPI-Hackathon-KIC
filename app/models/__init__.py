"""SIMOSI SQLModel ORM models.

All 18 tables mapped across 5 domain modules:
- device:         Device, DeviceConfig, DeviceState, DeviceCommand, DeviceLog
- sensor:         SensorDefinition, SensorParameter, DeviceSensor, CalibrationProfile, SensorThreshold
- reading:        SensorReading, DebuTambang, GasTambang, EmisiAlatBerat
- classification: Classification, AIProcessLog
- alert:          Alert, NotificationLog
"""

from app.models.alert import Alert, NotificationLog
from app.models.classification import AIProcessLog, Classification
from app.models.device import Device, DeviceCommand, DeviceConfig, DeviceLog, DeviceState
from app.models.reading import DebuTambang, EmisiAlatBerat, GasTambang, SensorReading
from app.models.sensor import (
    CalibrationProfile,
    DeviceSensor,
    SensorDefinition,
    SensorParameter,
    SensorThreshold,
)


__all__ = [
    # Device management
    "Device",
    "DeviceConfig",
    "DeviceState",
    "DeviceCommand",
    "DeviceLog",
    # Sensor catalog
    "SensorDefinition",
    "SensorParameter",
    "DeviceSensor",
    "CalibrationProfile",
    "SensorThreshold",
    # Reading data (Header-Detail)
    "SensorReading",
    "DebuTambang",
    "GasTambang",
    "EmisiAlatBerat",
    # AI & Classification
    "Classification",
    "AIProcessLog",
    # Alerting & Notification
    "Alert",
    "NotificationLog",
]
