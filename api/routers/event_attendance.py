from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.events_space import AttendanceCreate, AttendanceRead
from crud import crud_event_attendance
from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from dependencies.dependency import Dependency

router = APIRouter(prefix="/events", tags=["EventAttendance"])

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_dependency(db: Session = Depends(get_db)) -> Dependency:
    return Dependency(db)


def get_auth_dependency(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


@router.post("/{event_id}/attendance", response_model=AttendanceRead)
def register_attendance(
    event_id: int, data: AttendanceCreate, db: Session = Depends(get_db)
):
    try:
        return crud_event_attendance.create_attendance(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/attendance/{attendance_id}", response_model=AttendanceRead)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = crud_event_attendance.get_attendance(db, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance


@router.get("/attendance/", response_model=list[AttendanceRead])
def list_attendances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_event_attendance.get_all_attendances(db, skip=skip, limit=limit)


@router.delete("/attendance/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    # ADMIN_DASHBOARD still bypasses this check; anyone entrusted with
    # VIEW_REGISTRATIONS (e.g. the Finance role) can also manage attendance.
    auth_dependency.secure_access("VIEW_REGISTRATIONS", current_user["user_id"])
    success = crud_event_attendance.delete_attendance(db, attendance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return {"detail": "Attendance deleted"}


@router.delete("/{event_id}/attendance")
def delete_event_attendance(
    event_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_REGISTRATIONS", current_user["user_id"])
    count = crud_event_attendance.delete_all_attendance(db, event_id)
    return {"detail": f"Deleted {count} attendance record(s)"}
