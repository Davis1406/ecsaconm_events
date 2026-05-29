from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    auth,
    users,
    roles,
    permissions,
    countries,
    org_units,
    events,
    dashboard,
    event_attendance,
    registrations,
    abstracts,
    event_types,
    organisers,
    participants,
    email_templates,
    system_settings,
)

app = FastAPI(
    title="ECSACONM Events API Documentation",
    description="The ECSACONM Events API is an API for ECSACONM Events Management System.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Joel",
        "url": "https://github.com/jkumwenda",
        "email": "jkumwenda@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# ✅ Mount after FastAPI is initialized
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = [
    "https://events.ecsaconm.org",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, tags=["Auth"], prefix="/auth")
app.include_router(dashboard.router, tags=["Dashboard"], prefix="/dashboard")
app.include_router(users.router, tags=["Users"], prefix="/users")
app.include_router(roles.router, tags=["Roles"], prefix="/roles")
app.include_router(permissions.router, tags=["Permissions"], prefix="/permissions")
app.include_router(countries.router, tags=["Countries"], prefix="/countries")
app.include_router(org_units.router, tags=["Org units"], prefix="/org_units")
app.include_router(events.router, tags=["Events"], prefix="/events")
app.include_router(
    event_attendance.router, tags=["Event attendance"], prefix="/event_attendance"
)
app.include_router(
    registrations.router, tags=["Registrations"], prefix="/registrations"
)
app.include_router(abstracts.router, prefix="/abstracts", tags=["abstracts"])
app.include_router(event_types.router, prefix="/event_types", tags=["Event Types"])
app.include_router(organisers.router, prefix="/organisers", tags=["Organisers"])
app.include_router(participants.router, prefix="/participants", tags=["Participants"])
app.include_router(email_templates.router, prefix="/email_templates", tags=["Email Templates"])
app.include_router(system_settings.router, prefix="/system", tags=["System Settings"])
