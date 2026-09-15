# ECSACONM Events — System Design Document

**Version:** 1.0
**Date:** August 2026
**Project:** ECSACONM Events Portal (conference registration & abstract management)
**Production:** https://events.ecsaconm.org

---

## 1. Overview

The ECSACONM Events Portal is a web-based conference management system used by the
East, Central and Southern African College of Nursing and Midwifery (ECSACONM). It
handles the full lifecycle of a scientific conference:

- Public event pages & registration
- Online payment
- Abstract submission and review
- Abstract acceptance / notification of presenters
- Conference attendance confirmation
- Presentation (slide) upload and management

This document describes the system architecture, technology choices, data model,
API surface, frontend structure, and the workflow-specific features (abstract import
and registration reminders) added for the 17th ECSACONM Biennial Scientific
Conference & 8th General Assembly.

---

## 2. Architecture Overview

The system is a classic **two-tier web application** split into a separate frontend
SPA and a REST API, communicating over HTTP + JSON. The frontend is a static build
that can be served from any web server; the API is backed by a relational database.

```
┌─────────────────┐      HTTPS / JSON      ┌──────────────────┐        ┌─────────────┐
│  Vue 3 SPA      │  ───────────────────▶ │  FastAPI (Python) │  ────▶ │  MySQL       │
│  (Vite build)   │                        │  (API layer)      │        │  (SQLAlchemy)│
└─────────────────┘                        └──────────────────┘        └─────────────┘
        │                                          │
   Auth: JWT bearer token                  Email: SMTP via mailer_util
```

### 2.1 High-level components

| Component     | Technology        | Responsibility                                        |
|---------------|-------------------|-------------------------------------------------------|
| Frontend SPA  | Vue 3, Vite       | Public site, auth flows, admin dashboard, my-account |
| Backend API   | Python FastAPI    | REST endpoints, auth, RBAC, business logic            |
| ORM           | SQLAlchemy        | Object-relational mapping & migrations (Alembic)      |
| Database      | MySQL             | Persistence of all domain data                        |
| Email         | `smtplib`         | Registration confirmations, receipts, reminders       |
| Auth          | JWT (HS256)       | Stateless bearer tokens + permission checks           |

### 2.2 Repository layout

```
ecsaconm_events_src/
├── api/                      # FastAPI backend
│   ├── main.py               # App factory, CORS, router registration
│   ├── core/                 # config.py, database.py (engine/session)
│   ├── dependencies/         # auth_dependency.py, dependency.py
│   ├── models/models.py      # SQLAlchemy models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── routers/              # One module per resource
│   ├── crud/                 # Reusable query helpers
│   ├── utils/                # mailer_util.py, receipt_generator.py
│   ├── scripts/              # import_abstracts.py, download_drive_files.py
│   ├── seed_*.py             # role & permission seeding
│   └── alembic/              # DB migrations
├── web_vue/                  # Vue 3 frontend source (Vite)
│   └── src/
│       ├── views/            # Page components
│       ├── layouts/          # MainLayout, MyAccountLayout, WebLayout
│       ├── includes/         # Sidebar, Header, Footer
│       ├── components/       # Reusable modals / widgets
│       ├── store/            # Pinia stores (authStore, etc.)
│       └── router/index.js   # Routes + guards
├── web/                      # Production build output (compiled SPA)
├── setup_database.sql        # Initial database bootstrap
└── design.md                 # This document
```

---

## 3. Technology Stack

### 3.1 Backend — FastAPI (Python 3)

- **FastAPI** — async-capable REST framework with OpenAPI docs at `/docs`
- **SQLAlchemy 2.x** — ORM; MySQL via `pymysql`
- **Alembic** — schema migrations
- **Pydantic v2** — request/response validation
- **PyJWT** — HS256 JWT access tokens
- **python-multipart** — OAuth2 password form login
- **smtplib / email** — outbound email
- **openpyxl / odfpy** — reading Excel / ODS spreadsheets for import

Key runtime values are read from `api/.env` (database URL, JWT secret,
`CLIENT_ORIGIN`, SMTP credentials).

### 3.2 Frontend — Vue 3 (Options API)

- **Vue 3** with **Options API** (no `<script setup>` / Composition API)
- **Vite** build tooling; dev server on port 5174
- **Vue Router 4** — lazy-loaded route components, auth guards
- **Pinia** — auth store (user, permissions, token)
- **Tailwind CSS** — utility-first styling
- **Heroicons** — icon set
- **Axios** — HTTP client (`fetchData` / `this._api()` helpers)

**Design conventions**
- Brand colours: `rgb(254, 80, 103)` (primary) and `rgb(220, 50, 75)` (hover/accent)
- Font: Roboto (`font-roboto`)
- Admin UI: sidebar (fixed) + scrollable main area
- All API calls go through a shared fetch wrapper so the bearer token is attached
  automatically and errors are handled centrally

---

## 4. Authentication & Authorization

### 4.1 Login flow

1. Client POSTs `username` + `password` to `POST /auth/login`
   (OAuth2 password form).
2. Backend verifies the user, issues a JWT (HS256) with the configured
   `SECRET_KEY` + `ALGORITHM` env vars.
3. Client stores the token and a permissions array in the Pinia auth store.
4. Subsequent requests send `Authorization: Bearer <token>`.

### 4.2 Role-based access control (RBAC)

- **Users** belong to **Roles**; roles grant **Permissions**.
- Permissions are named like `VIEW_ABSTRACTS`, `ADMIN_DASHBOARD`, `VIEW_EVENT`,
  `VIEW_USER`, etc.
- Backend dependencies (`user_dependency`, `get_auth_dep()`) validate the token and
  check the required permission per endpoint.
- The frontend Sidebar filters menu items using `permissionCodes` from the auth store.

### 4.3 Password handling

- Passwords hashed with **bcrypt** (`passlib`).
- Flows for registration, set-password (first login), and reset-password.

---

## 5. Data Model

Core entities (`api/models/models.py`):

| Entity                 | Purpose                                                        |
|------------------------|----------------------------------------------------------------|
| `User`                 | Accounts (admins, participants, presenters)                    |
| `Role` / `Permission`  | RBAC groups and granular permissions                           |
| `UserRole`             | User–role link table                                           |
| `Event`                | Conferences (e.g. 17th Biennial)                               |
| `EventType`            | Classification of events                                       |
| `Organiser`            | Organisations running events                                   |
| `Participant`          | Registration records for an event                              |
| `Registration`         | Enrollment of a user in an event                               |
| `Abstract`             | Submitted scientific abstracts                                 |
| `AbstractAuthor`       | Presenting author + co-authors of an abstract                  |
| `AbstractStatus`       | Acceptance status (e.g. accept oral / accept poster)           |
| `PresentationTemplate` | Downloadable slide templates                                   |
| `UploadedPresentation` | Presenters' uploaded slide files                               |
| `Country`, `OrgUnit`, etc. | Lookup / organisational data                               |
| `EmailTemplate`        | Configurable email body templates                              |
| `SystemSetting`        | Runtime configuration (SMTP, links, etc.)                      |

### 5.1 Abstract / author relationship

```
Abstract 1 ──── * AbstractAuthor
                 * Author has: full_name, email, is_presenting
```

Each abstract has exactly one presenting author (the submitter's email match, or the
first author when no account matches) and up to eight co-authors. Presenters are
deduplicated by email across the whole conference for reminder purposes.

---

## 6. API Surface

Routers (`api/routers/`): `auth`, `users`, `roles`, `permissions`, `events`,
`event_types`, `registrations`, `participants`, `abstracts`, `organisers`,
`organisations`, `countries`, `dashboard`, `email_templates`, `system_settings`,
`event_attendance`, `presentation_templates`.

### 6.1 Auth
- `POST /auth/login` — OAuth2 form login → JWT + permissions
- `POST /auth/register`, set/reset password endpoints

### 6.2 Abstracts (admin)
| Method | Path                                             | Purpose                                   |
|--------|--------------------------------------------------|-------------------------------------------|
| GET    | `/abstracts`                                     | List abstracts (search / paginate)        |
| GET    | `/abstracts/{id}`                                | Detail incl. authors                       |
| GET    | `/abstracts/registration-reminder-preview`       | List presenters not yet registered        |
| POST   | `/abstracts/send-registration-reminders`         | Email reminders to unregistered presenters|
| POST   | `/abstracts/import`                              | Bulk import from spreadsheet (script-based)|

> Router convention: **literal paths are registered before parameterised paths**
> (`/abstracts/registration-reminder-preview` must precede `/abstracts/{id}`), and
> related models are eager-loaded with `joinedload()`.

### 6.3 Registration-reminder flow (added feature)

1. **Preview** (`GET /abstracts/registration-reminder-preview?event_id=1`)
   - Requires `VIEW_ABSTRACTS` permission.
   - Loads all abstracts + authors for the event.
   - Deduplicates presenters by email.
   - Filters out any presenter who already has a user account that is registered
     for the event.
   - Returns the remaining list (presenter name, email, abstract count/status).
2. **Send** (`POST /abstracts/send-registration-reminders?event_id=1`)
   - Requires the same permission.
   - Recomputes the same recipient list server-side (never trusts client input).
   - Enqueues `mailer_util.registration_reminder_email(...)` per recipient via
     FastAPI `BackgroundTasks` so the HTTP response returns immediately.
   - Returns `{ total_sent, recipients: [...] }`.

---

## 7. Frontend Structure

### 7.1 Layouts

| Layout            | Used for                                 |
|-------------------|------------------------------------------|
| `WebLayout`       | Public site (home, events, register)     |
| `MainLayout`      | Authenticated admin area (sidebar)       |
| `MyAccountLayout` | Logged-in participant dashboard          |

### 7.2 Admin views

- `main/dashboard/Dashboard.vue`
- `main/events/` — list, detail, add, edit, access/registration modal
- `main/registrations/Registrations.vue`
- `main/attendance/AttendanceConfirmation.vue`
- `main/abstracts/`
  - `Abstracts.vue` — list & search
  - `Abstract.vue` — detail with authors/status
  - `AbstractNotifications.vue` — **registration reminders UI (new)**
  - `PresentationTemplates.vue` — slide template management
  - `UploadedPresentations.vue` — uploaded slide review
- `main/participants/` — participant CRUD
- `main/configurations/` — users, roles, event types, organisers, contacts,
  email templates

### 7.3 AbstractNotifications.vue (new)

- Options-API component using `HeaderView`, `SpinnerComponent`, `fetchData`.
- On mount, calls the **preview** endpoint for the active event.
- Renders a table of unregistered presenters with name, email, and an
  "Account" badge indicating whether a matching user account exists.
- Buttons:
  - **Refresh** — re-fetch the preview list.
  - **Send Reminders** — POSTs to the send endpoint and shows the response
    (`total_sent`, recipients).
- Route registered lazily as `AbstractNotificationsView`; reachable via the
  "Notifications" item in the **Abstracts** section of the sidebar.

### 7.4 Routing

- Lazy-loaded components (`() => import('...')`).
- `abstractRoutes` computed list in `Sidebar.vue` highlights the current section
  (includes `Abstracts`, `Abstract`, `AbstractNotifications`,
  `PresentationTemplates`, `UploadedPresentations`).
- Navigation guards enforce authentication where required.

---

## 8. Abstract Import Feature

### 8.1 Source data

- File: `All-Abstracts.xlsx.ods` (ODF spreadsheet), 233 accepted abstracts.
- Columns: title, abstract body (`Description`), track (`Topic`), acceptance status
  ("Accept for oral" / "Accept for poster"), and up to eight author columns
  (`Author Email_1` … `Author Email_8`).

### 8.2 Import script (`api/scripts/import_abstracts.py`)

- **Idempotent:** skips any abstract whose title already exists in the DB, so
  re-running never duplicates data.
- For each row:
  1. Create `Abstract` with title, abstract text, track, and acceptance status
     mapped to an `AbstractStatus`.
  2. Determine the **presenting author** — the email that matches an existing
     user account; otherwise the first author.
  3. Parse each author's full name (`parse_name()` splits on the last space into
     first/last names) and create `AbstractAuthor` rows (presenting + co-authors).
  4. Set `submitted_by` to the matched user id, or admin id `1` when no account
     exists.
- Run: `python api/scripts/import_abstracts.py`

### 8.3 Post-import state (local reference)

- 346 abstracts total (239 oral, 107 poster); 615 `abstract_author` rows.
- Only **8** presenter emails matched existing accounts at import time; 225 did
  not — these are the target audience for the registration-reminder feature.

---

## 9. Email / Notifications

- `api/utils/mailer_util.py` builds and sends HTML emails via SMTP
  (host, port, username, password from settings/.env).
- Email types: registration confirmation, payment receipt, set-password,
  reset-password, and **registration reminder** (new).
- The registration-reminder email prompts presenters to register for the event and
  upload their presentation; links back to the public registration page
  (`CLIENT_ORIGIN`).

---

## 10. Security

- Passwords: bcrypt hashes; never stored or logged in plain text.
- API: JWT bearer tokens; per-endpoint permission enforcement.
- CORS: restricted to configured `CLIENT_ORIGIN`.
- Reminder lists are recomputed server-side; the client cannot spoof recipients.
- Secrets (JWT secret, DB credentials, SMTP credentials) live in `.env` and are
  excluded from version control (`.gitignore`).

---

## 11. Deployment

### 11.1 Local development

1. Start MySQL (XAMPP).
2. `mysql -u root < setup_database.sql` (bootstrap DB).
3. `alembic upgrade head` (migrations).
4. `python seed_roles.py && python seed_permissions.py` (optional seeding).
5. `uvicorn main:app --reload --port 8001` → docs at `http://localhost:8001/docs`.
6. `npm run dev` in `web_vue/` → app at `http://localhost:5174`.

### 11.2 Production

- Backend deployed to an AWS EC2 instance (e.g. `/var/www/ecsaconm_events/`).
- Frontend built with Vite (`npm run build`) and the static `web/` output served
  by a web server / CDN.
- Environment variables configured on the server (database, JWT, SMTP, origins).
- Push source to GitHub (`https://github.com/Davis1406/ecsaconm_events.git`) and
  pull on the server, then rebuild.

### 11.3 Rollout checklist for new features

1. Implement in the source repo, test against local API (port 8001) and frontend
   (port 5174).
2. Verify against the local database (`ecsaconm_events`, root/root via XAMPP).
3. Push to GitHub.
4. Pull on production and rebuild frontend + restart API.
5. Smoke-test the production domain.

---

## 12. Known Conventions & Gotchas

- **Options API only** in Vue — do not introduce `<script setup>` or
  Composition-API refs.
- Sidebar/brand colours must use `rgb(254,80,103)` / `rgb(220,50,75)`.
- Backend literal route paths must be declared before dynamic `/{id}` paths.
- Prefer `joinedload()` for relationships used in list/detail responses.
- The JWT secret env vars are `SECRET_KEY` + `ALGORITHM` (HS256); the RSA
  keypair vars in `.env` are not used by auth.
- Re-running `import_abstracts.py` is safe (skips existing titles).

---

## 13. Future / Roadmap

- Add an admin "add/edit participant" page linking presenters without accounts to
  new user records.
- Make email templates for reminders editable via the existing
  `EmailTemplates` configuration.
- Dashboard stats for abstract acceptance by track.
- Scheduled (cron) reminder dispatch instead of manual button trigger.
