from datetime import date, datetime, time
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Date
from models.models import (
    EventAttendance,
    Registration,
)  # Make sure Registration model is imported
from schemas.events_space import AttendanceCreate


def create_attendance(db: Session, data: AttendanceCreate):
    target_date = data.attendance_date or date.today()

    # Check if the registration exists
    registration = (
        db.query(Registration).filter(Registration.id == data.registration_id).first()
    )
    if not registration:
        raise ValueError("User not registered")

    # Check if attendance already exists for this registration on the target date
    existing = (
        db.query(EventAttendance)
        .filter(
            EventAttendance.registration_id == data.registration_id,
            EventAttendance.attendance_date.cast(Date) == target_date,
        )
        .first()
    )
    if existing:
        raise ValueError("Attendance already recorded for this date")

    attendance = EventAttendance(
        registration_id=data.registration_id,
        attendance_date=datetime.combine(target_date, time.min),
    )
    db.add(attendance)
    try:
        db.commit()
        db.refresh(attendance)
        return attendance
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database error while recording attendance: {str(e.orig)}")


def get_attendance(db: Session, attendance_id: int):
    return db.query(EventAttendance).filter(EventAttendance.id == attendance_id).first()


def get_all_attendances(db: Session, skip: int = 0, limit: int = 100):
    return db.query(EventAttendance).offset(skip).limit(limit).all()


def delete_attendance(db: Session, attendance_id: int):
    attendance = (
        db.query(EventAttendance).filter(EventAttendance.id == attendance_id).first()
    )
    if attendance:
        db.delete(attendance)
        db.commit()
        return True
    return False


def delete_all_attendance(db: Session, event_id: int):
    """Delete every attendance record belonging to an event's registrations.
    Returns the number of records removed."""
    reg_ids = [
        r.id
        for r in db.query(Registration)
        .filter(Registration.event_id == event_id)
        .all()
    ]
    if not reg_ids:
        return 0
    count = (
        db.query(EventAttendance)
        .filter(EventAttendance.registration_id.in_(reg_ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return count
