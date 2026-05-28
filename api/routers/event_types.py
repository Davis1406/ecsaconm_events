from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth_dependency import get_current_user
from models.models import EventType

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/")
def get_event_types(
    user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: str = "",
):
    query = db.query(EventType).filter(EventType.deleted_at == None)
    if search:
        query = query.filter(EventType.event_type.ilike(f"%{search}%"))
    total = query.count()
    items = query.offset(skip).limit(limit if limit else total).all()
    return {"data": items, "total": total}


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_event_type(
    user: user_dependency,
    payload: dict,
    db: Session = Depends(get_db),
):
    item = EventType(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{id}")
def get_event_type(id: int, user: user_dependency, db: Session = Depends(get_db)):
    item = db.query(EventType).filter(EventType.id == id, EventType.deleted_at == None).first()
    if not item:
        raise HTTPException(status_code=404, detail="Event type not found")
    return item


@router.put("/{id}")
def update_event_type(id: int, user: user_dependency, payload: dict, db: Session = Depends(get_db)):
    item = db.query(EventType).filter(EventType.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Event type not found")
    for k, v in payload.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_type(id: int, user: user_dependency, db: Session = Depends(get_db)):
    from datetime import datetime, timezone
    item = db.query(EventType).filter(EventType.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Event type not found")
    item.deleted_at = datetime.now(timezone.utc)
    db.commit()
