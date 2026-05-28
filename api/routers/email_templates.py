from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from core.database import get_db
from models.models import EmailTemplate
from dependencies.auth_dependency import Auth, get_current_user
from dependencies.dependency import Dependency
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]


def get_auth_dependency(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


class EmailTemplateUpdateSchema(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body_html: Optional[str] = None


@router.get("")
@router.get("/")
async def list_email_templates(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    templates = db.query(EmailTemplate).order_by(EmailTemplate.id).all()
    return {
        "data": [
            {
                "id": t.id,
                "template_key": t.template_key,
                "name": t.name,
                "subject": t.subject,
                "variables": t.variables,
                "updated_at": t.updated_at,
            }
            for t in templates
        ]
    }


@router.get("/{template_key}")
async def get_email_template(
    template_key: str,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    t = db.query(EmailTemplate).filter_by(template_key=template_key).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": t.id,
        "template_key": t.template_key,
        "name": t.name,
        "subject": t.subject,
        "body_html": t.body_html,
        "variables": t.variables,
        "updated_at": t.updated_at,
    }


@router.put("/{template_key}")
async def update_email_template(
    template_key: str,
    schema: EmailTemplateUpdateSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    t = db.query(EmailTemplate).filter_by(template_key=template_key).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    if schema.name is not None:
        t.name = schema.name
    if schema.subject is not None:
        t.subject = schema.subject
    if schema.body_html is not None:
        t.body_html = schema.body_html
        # Sync back to file so live emails use updated template
        import os
        fname_map = {
            "account_creation": "acount_creation_template.html",
            "password_reset_request": "password_reset_request_template.html",
            "password_reset": "password_reset_template.html",
            "account_verification_request": "account_verification_request_template.html",
            "account_verification": "account_verification_template.html",
        }
        fname = fname_map.get(template_key)
        if fname:
            fpath = os.path.join("templates", fname)
            try:
                with open(fpath, "w") as f:
                    f.write(schema.body_html)
            except Exception as e:
                pass  # DB is source of truth; file sync is best-effort
    db.commit()
    db.refresh(t)
    return {"message": "Template updated successfully", "template_key": template_key}
