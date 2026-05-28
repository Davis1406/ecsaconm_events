import json
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel
from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]

CONTACTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'contacts.json')


def get_auth_dependency(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


class ContactsSchema(BaseModel):
    address_line1: Optional[str] = ""
    address_line2: Optional[str] = ""
    phone1: Optional[str] = ""
    phone2: Optional[str] = ""
    fax: Optional[str] = ""
    email_general: Optional[str] = ""
    email_conference: Optional[str] = ""
    website: Optional[str] = ""


def read_contacts() -> dict:
    try:
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {
            "address_line1": "",
            "address_line2": "",
            "phone1": "",
            "phone2": "",
            "fax": "",
            "email_general": "",
            "email_conference": "",
            "website": "",
        }


def write_contacts(data: dict):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@router.get("/contacts")
async def get_contacts():
    """Public endpoint — no auth required so the Contacts page can show to all."""
    return read_contacts()


@router.put("/contacts")
async def update_contacts(
    contacts: ContactsSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    write_contacts(contacts.dict())
    return {"detail": "Contacts updated successfully"}
