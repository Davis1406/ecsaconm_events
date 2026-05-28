"""
Seed script for ECSACONM Events database.
Run from the api directory: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.models import (
    Country, OrgUnit, OrgUnitType, Role, Permission, RolePermission, User, UserRole,
    EventType, Organiser, Event
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def seed():
    db: Session = SessionLocal()
    try:
        # ── 1. Countries (ECSA member states + common) ──────────────────────
        countries_data = [
            {"country": "Botswana",      "short_code": "BW", "category": "african"},
            {"country": "Eswatini",      "short_code": "SZ", "category": "african"},
            {"country": "Ethiopia",      "short_code": "ET", "category": "african"},
            {"country": "Kenya",         "short_code": "KE", "category": "african"},
            {"country": "Lesotho",       "short_code": "LS", "category": "african"},
            {"country": "Malawi",        "short_code": "MW", "category": "african"},
            {"country": "Mauritius",     "short_code": "MU", "category": "african"},
            {"country": "Mozambique",    "short_code": "MZ", "category": "african"},
            {"country": "Namibia",       "short_code": "NA", "category": "african"},
            {"country": "Rwanda",        "short_code": "RW", "category": "african"},
            {"country": "Seychelles",    "short_code": "SC", "category": "african"},
            {"country": "Somalia",       "short_code": "SO", "category": "african"},
            {"country": "South Sudan",   "short_code": "SS", "category": "african"},
            {"country": "Sudan",         "short_code": "SD", "category": "african"},
            {"country": "Tanzania",      "short_code": "TZ", "category": "african"},
            {"country": "Uganda",        "short_code": "UG", "category": "african"},
            {"country": "Zambia",        "short_code": "ZM", "category": "african"},
            {"country": "Zimbabwe",      "short_code": "ZW", "category": "african"},
            {"country": "South Africa",  "short_code": "ZA", "category": "african"},
            {"country": "United Kingdom","short_code": "GB", "category": "non_african"},
            {"country": "United States", "short_code": "US", "category": "non_african"},
            {"country": "India",         "short_code": "IN", "category": "non_african"},
            {"country": "China",         "short_code": "CN", "category": "non_african"},
        ]
        country_map = {}
        for c in countries_data:
            existing = db.query(Country).filter(Country.country == c["country"]).first()
            if not existing:
                obj = Country(**c)
                db.add(obj)
                db.flush()
                country_map[c["country"]] = obj.id
            else:
                country_map[c["country"]] = existing.id
        db.commit()
        print(f"✓ {len(countries_data)} countries seeded")

        # ── 2. Org Unit ──────────────────────────────────────────────────────
        org_unit_name = "ECSACONM Secretariat"
        existing_org = db.query(OrgUnit).filter(OrgUnit.name == org_unit_name).first()
        if not existing_org:
            org = OrgUnit(
                name=org_unit_name,
                type=OrgUnitType.secretariat,
                description="Eastern, Central and Southern Africa College of Nursing and Midwifery Secretariat",
            )
            db.add(org)
            db.flush()
            org_unit_id = org.id
        else:
            org_unit_id = existing_org.id
        db.commit()
        print(f"✓ Org unit seeded: {org_unit_name}")

        # ── 3. Roles ─────────────────────────────────────────────────────────
        roles_data = [
            {"role": "Admin",   "description": "System administrator with full access"},
            {"role": "Manager", "description": "Event manager"},
            {"role": "User",    "description": "Regular user / delegate"},
        ]
        role_map = {}
        for r in roles_data:
            existing = db.query(Role).filter(Role.role == r["role"]).first()
            if not existing:
                obj = Role(**r)
                db.add(obj)
                db.flush()
                role_map[r["role"]] = obj.id
            else:
                role_map[r["role"]] = existing.id
        db.commit()
        print(f"✓ {len(roles_data)} roles seeded")

        # ── 4. Permissions ───────────────────────────────────────────────────
        permissions_data = [
            ("ADMIN_DASHBOARD",      "ECSACONM", "Admin Dashboard"),
            ("ADD_USER",             "ECSACONM", "Add User"),
            ("VIEW_USER",            "ECSACONM", "View User"),
            ("UPDATE_USER",          "ECSACONM", "Update User"),
            ("DELETE_USER",          "ECSACONM", "Delete User"),
            ("ADD_ROLE",             "ECSACONM", "Add Role"),
            ("VIEW_ROLE",            "ECSACONM", "View Role"),
            ("UPDATE_ROLE",          "ECSACONM", "Update Role"),
            ("DELETE_ROLE",          "ECSACONM", "Delete Role"),
            ("ADD_PERMISSION",       "ECSACONM", "Add Permission"),
            ("VIEW_PERMISSION",      "ECSACONM", "View Permission"),
            ("UPDATE_PERMISSION",    "ECSACONM", "Update Permission"),
            ("DELETE_PERMISSION",    "ECSACONM", "Delete Permission"),
            ("ADD_EVENT",            "ECSACONM", "Add Event"),
            ("VIEW_EVENT",           "ECSACONM", "View Event"),
            ("UPDATE_EVENT",         "ECSACONM", "Update Event"),
            ("DELETE_EVENT",         "ECSACONM", "Delete Event"),
            ("ADD_ORG_UNIT",         "ECSACONM", "Add Org Unit"),
            ("VIEW_ORG_UNIT",        "ECSACONM", "View Org Unit"),
            ("UPDATE_ORG_UNIT",      "ECSACONM", "Update Org Unit"),
            ("DELETE_ORG_UNIT",      "ECSACONM", "Delete Org Unit"),
            ("ADD_ORGANISATION",     "ECSACONM", "Add Organisation"),
            ("VIEW_ORGANISATION",    "ECSACONM", "View Organisation"),
            ("VIEW_ABSTRACTS",       "ECSACONM", "View Abstracts"),
            ("EXPORT_ABSTRACTS",     "ECSACONM", "Export Abstracts"),
            ("MANAGE_REVIEWERS",     "ECSACONM", "Manage Reviewers"),
            ("VIEW_REGISTRATIONS",   "ECSACONM", "View Registrations"),
            ("EXPORT_REGISTRATIONS", "ECSACONM", "Export Registrations"),
        ]
        permission_map = {}
        for code, sys_code, name in permissions_data:
            existing = db.query(Permission).filter(Permission.permission_code == code).first()
            if not existing:
                obj = Permission(permission=name, permission_code=code, system_code=sys_code)
                db.add(obj)
                db.flush()
                permission_map[code] = obj.id
            else:
                permission_map[code] = existing.id
        db.commit()
        print(f"✓ {len(permissions_data)} permissions seeded")

        # ── 5. Admin User ────────────────────────────────────────────────────
        admin_email = "admin@ecsaconm.org"
        existing_user = db.query(User).filter(User.email == admin_email).first()
        if not existing_user:
            admin = User(
                firstname="ECSACONM",
                lastname="Admin",
                email=admin_email,
                phone="+255000000000",
                hashed_password=hash_password("Admin@2026!"),
                verified=True,
            )
            db.add(admin)
            db.flush()
            admin_id = admin.id

            admin_role_id = role_map.get("Admin")
            if admin_role_id:
                ur = UserRole(user_id=admin_id, role_id=admin_role_id)
                db.add(ur)
            db.commit()
            print(f"✓ Admin user created: {admin_email} / Admin@2026!")
        else:
            admin_id = existing_user.id
            print(f"✓ Admin user already exists: {admin_email}")

        # ── 5b. Assign ALL permissions to Admin role ─────────────────────────
        admin_role_id = role_map.get("Admin")
        if admin_role_id and permission_map:
            for perm_id in permission_map.values():
                exists = db.query(RolePermission).filter(
                    RolePermission.role_id == admin_role_id,
                    RolePermission.permission_id == perm_id
                ).first()
                if not exists:
                    db.add(RolePermission(role_id=admin_role_id, permission_id=perm_id))
            db.commit()
            print(f"✓ All {len(permission_map)} permissions assigned to Admin role")

        # ── 6. Event Types ───────────────────────────────────────────────────
        event_types_data = [
            {"event_type": "Biennial Scientific Conference",
             "description": "ECSACONM biennial scientific conference held every two years"},
            {"event_type": "General Assembly",
             "description": "General assembly of ECSACONM member states"},
            {"event_type": "Workshop",
             "description": "Skills and capacity building workshop"},
            {"event_type": "Seminar",
             "description": "Educational seminar"},
            {"event_type": "Symposium",
             "description": "Academic symposium"},
        ]
        event_type_map = {}
        for et in event_types_data:
            existing = db.query(EventType).filter(EventType.event_type == et["event_type"]).first()
            if not existing:
                obj = EventType(**et)
                db.add(obj)
                db.flush()
                event_type_map[et["event_type"]] = obj.id
            else:
                event_type_map[et["event_type"]] = existing.id
        db.commit()
        print(f"✓ {len(event_types_data)} event types seeded")

        # ── 7. Organisers ────────────────────────────────────────────────────
        organisers_data = [
            {"organiser": "ECSACONM",
             "description": "Eastern, Central and Southern Africa College of Nursing and Midwifery"},
            {"organiser": "Tanzania Nurses and Midwives Council",
             "description": "Regulatory body for nursing and midwifery in Tanzania"},
        ]
        organiser_map = {}
        for org in organisers_data:
            existing = db.query(Organiser).filter(Organiser.organiser == org["organiser"]).first()
            if not existing:
                obj = Organiser(**org)
                db.add(obj)
                db.flush()
                organiser_map[org["organiser"]] = obj.id
            else:
                organiser_map[org["organiser"]] = existing.id
        db.commit()
        print(f"✓ {len(organisers_data)} organisers seeded")

        # ── 8. 17th ECSACONM Biennial Scientific Conference ─────────────────
        conf_title = "17th ECSACONM Biennial Scientific Conference"
        existing_event = db.query(Event).filter(Event.event == conf_title).first()
        if not existing_event:
            event = Event(
                event=conf_title,
                theme="Nurses and Midwives Sustaining Quality Healthcare in a Changing World",
                description=(
                    "The 17th ECSACONM Biennial Scientific Conference brings together nursing and "
                    "midwifery professionals from Eastern, Central and Southern Africa to share "
                    "knowledge, research, and best practices in healthcare delivery. "
                    "Hosted in Zanzibar, Tanzania, the conference will focus on innovative "
                    "approaches to sustaining quality healthcare amid a rapidly changing world."
                ),
                location="Zanzibar, Tanzania",
                start_date=date(2026, 9, 14),
                end_date=date(2026, 9, 16),
                country_id=country_map.get("Tanzania"),
                event_type_id=event_type_map.get("Biennial Scientific Conference"),
                organiser_id=organiser_map.get("ECSACONM"),
                org_unit_id=org_unit_id,
                user_id=admin_id,
                capacity=500,
            )
            db.add(event)
            db.commit()
            print(f"✓ Event seeded: {conf_title}")
            print(f"  Location: Zanzibar, Tanzania | Dates: Sep 14-16, 2026")
        else:
            print(f"✓ Event already exists: {conf_title}")

        print("\n🎉 Seed complete!")

    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
