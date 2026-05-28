from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth_dependency import get_current_user
from models.models import Participant

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/")
def get_participants(
    user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: str = "",
    event_id: int = None,
):
    query = db.query(Participant).filter(Participant.deleted_at == None)
    if event_id:
        query = query.filter(Participant.event_id == event_id)
    if search:
        query = query.filter(
            Participant.firstname.ilike(f"%{search}%") |
            Participant.lastname.ilike(f"%{search}%") |
            Participant.email.ilike(f"%{search}%") |
            Participant.registration_number.ilike(f"%{search}%")
        )
    total = query.count()
    items = query.offset(skip).limit(limit if limit else total).all()
    return {"data": items, "total": total}


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_participant(
    user: user_dependency,
    payload: dict,
    db: Session = Depends(get_db),
):
    item = Participant(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{id}")
def get_participant(id: int, user: user_dependency, db: Session = Depends(get_db)):
    item = db.query(Participant).filter(Participant.id == id, Participant.deleted_at == None).first()
    if not item:
        raise HTTPException(status_code=404, detail="Participant not found")
    return item


@router.put("/{id}")
def update_participant(id: int, user: user_dependency, payload: dict, db: Session = Depends(get_db)):
    item = db.query(Participant).filter(Participant.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Participant not found")
    for k, v in payload.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(id: int, user: user_dependency, db: Session = Depends(get_db)):
    from datetime import datetime, timezone
    item = db.query(Participant).filter(Participant.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Participant not found")
    item.deleted_at = datetime.now(timezone.utc)
    db.commit()
