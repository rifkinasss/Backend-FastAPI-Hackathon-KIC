from datetime import datetime, timezone

from sqlmodel import Session, select

from app.core.postgresql import create_db_and_tables, get_postgres_engine
from app.models import Device, DeviceCommand, DeviceState


ALLOWED_COMMANDS = {"turn_off", "turn_on", "restart"}
TERMINAL_STATUSES = {"acknowledged", "failed"}


def ensure_tables():
    create_db_and_tables()


def ensure_device(session: Session, device_id: str, location: str | None = None):
    device = session.exec(select(Device).where(Device.device_id == device_id)).first()

    if device is None:
        device = Device(device_id=device_id, location=location)
        session.add(device)
        session.flush()
    elif location:
        device.location = location
        device.updated_at = datetime.now(timezone.utc)

    return device


def touch_device_state(
    session: Session,
    device_id: str,
    *,
    is_online: bool = True,
    location: str | None = None,
    power_state: str | None = None,
):
    ensure_device(session, device_id, location)
    now = datetime.now(timezone.utc)
    state = session.exec(
        select(DeviceState).where(DeviceState.device_id == device_id)
    ).first()

    if state is None:
        state = DeviceState(
            device_id=device_id,
            is_online=is_online,
            last_seen_at=now if is_online else None,
            power_state=power_state or "on",
            updated_at=now,
        )
        session.add(state)
    else:
        state.is_online = is_online
        state.updated_at = now
        if is_online:
            state.last_seen_at = now
        if power_state:
            state.power_state = power_state

    return state


def create_device_command(device_id: str, command: str, requested_by: str | None = None):
    ensure_tables()
    normalized_command = command.strip().lower()
    if normalized_command not in ALLOWED_COMMANDS:
        raise ValueError("command harus salah satu dari: turn_off, turn_on, restart")

    with Session(get_postgres_engine()) as session:
        ensure_device(session, device_id)
        row = DeviceCommand(
            device_id=device_id,
            command=normalized_command,
            requested_by=requested_by,
            status="pending",
        )
        session.add(row)

        state = touch_device_state(session, device_id, is_online=True)
        state.last_command_at = datetime.now(timezone.utc)

        session.commit()
        session.refresh(row)

    return serialize_command(row)


def get_next_device_command(device_id: str):
    ensure_tables()

    with Session(get_postgres_engine()) as session:
        touch_device_state(session, device_id, is_online=True)
        row = session.exec(
            select(DeviceCommand)
            .where(DeviceCommand.device_id == device_id)
            .where(DeviceCommand.status == "pending")
            .order_by(DeviceCommand.created_at)
        ).first()

        if row is not None:
            row.status = "sent"
            session.add(row)

        session.commit()
        if row is not None:
            session.refresh(row)

    return serialize_command(row) if row else None


def acknowledge_device_command(
    device_id: str,
    command_id: int,
    status: str,
    error_message: str | None = None,
):
    ensure_tables()
    normalized_status = status.strip().lower()
    if normalized_status not in TERMINAL_STATUSES:
        raise ValueError("status harus acknowledged atau failed")

    with Session(get_postgres_engine()) as session:
        row = session.exec(
            select(DeviceCommand)
            .where(DeviceCommand.id == command_id)
            .where(DeviceCommand.device_id == device_id)
        ).first()
        if row is None:
            raise LookupError("Command tidak ditemukan")

        row.status = normalized_status
        row.error_message = error_message
        row.acknowledged_at = datetime.now(timezone.utc)

        power_state = None
        if normalized_status == "acknowledged":
            if row.command == "turn_off":
                power_state = "off"
            elif row.command in {"turn_on", "restart"}:
                power_state = "on"

        state = touch_device_state(
            session,
            device_id,
            is_online=row.command != "turn_off" or normalized_status != "acknowledged",
            power_state=power_state,
        )
        state.last_command_at = datetime.now(timezone.utc)

        session.add(row)
        session.commit()
        session.refresh(row)

    return serialize_command(row)


def list_device_states():
    ensure_tables()

    with Session(get_postgres_engine()) as session:
        rows = session.exec(select(DeviceState).order_by(DeviceState.device_id)).all()

    return [serialize_state(row) for row in rows]


def update_state_from_reading(device_id: str, location: str | None = None):
    ensure_tables()

    with Session(get_postgres_engine()) as session:
        state = touch_device_state(
            session,
            device_id,
            is_online=True,
            location=location,
            power_state="on",
        )
        session.commit()
        session.refresh(state)

    return serialize_state(state)


def serialize_command(row: DeviceCommand):
    return {
        "id": row.id,
        "device_id": row.device_id,
        "command": row.command,
        "status": row.status,
        "requested_by": row.requested_by,
        "error_message": row.error_message,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "acknowledged_at": row.acknowledged_at.isoformat() if row.acknowledged_at else None,
    }


def serialize_state(row: DeviceState):
    return {
        "device_id": row.device_id,
        "is_online": row.is_online,
        "power_state": row.power_state,
        "last_seen_at": row.last_seen_at.isoformat() if row.last_seen_at else None,
        "last_command_at": row.last_command_at.isoformat() if row.last_command_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }
