# ECSACONM Events Portal — Team Guide

> Developer reference for system structure, local setup, version control, and deployment.
> Production: **https://events.ecsaconm.org**

---

## Table of Contents

1. [Tech Stack](#1-tech-stack)
2. [Repository Structure](#2-repository-structure)
3. [Local Development Setup](#3-local-development-setup)
4. [Environment Variables](#4-environment-variables)
5. [Version Control Workflow](#5-version-control-workflow)
6. [Deployment](#6-deployment)
7. [Server Infrastructure](#7-server-infrastructure)
8. [Database](#8-database)
9. [Common Tasks](#9-common-tasks)
10. [Coding Conventions](#10-coding-conventions)

---

## 1. Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vue 3 (Options API), Vite, Tailwind CSS v3, Pinia, Vue Router (hash mode) |
| **Backend** | FastAPI (Python 3.14), SQLAlchemy 2.0, Alembic, Uvicorn |
| **Database** | MariaDB — database `ecsaconm_events` |
| **Web server** | Nginx (reverse proxy + static file serving) |
| **Auth** | JWT (HS256) via `python-jose`; Pinia auth store persisted to localStorage |
| **Email** | SMTP via `mailer_util.py`; HTML templates in `api/templates/` |
| **File uploads** | Stored on-disk at `api/uploads/`; served directly by Nginx at `/uploads/` |
| **SSL** | Let's Encrypt, managed by Certbot |
| **Hosting** | AWS EC2 — `ec2-54-242-206-111.compute-1.amazonaws.com` |

---

## 2. Repository Structure

```
ecsaconm_events/
├── api/                        ← FastAPI backend
│   ├── main.py                 ← App entrypoint, router registration
│   ├── models/
│   │   └── models.py           ← All SQLAlchemy ORM models
│   ├── routers/                ← One file per resource group
│   │   ├── abstracts.py
│   │   ├── auth.py
│   │   ├── events.py
│   │   ├── registrations.py
│   │   ├── users.py
│   │   └── ...
│   ├── schemas/
│   │   └── events_space.py     ← Pydantic request/response schemas
│   ├── core/
│   │   ├── config.py           ← Settings (reads .env)
│   │   └── database.py         ← SQLAlchemy engine + session
│   ├── dependencies/
│   │   └── auth_dependency.py  ← JWT decode, Auth class (permission checks)
│   ├── utils/
│   │   ├── mailer_util.py      ← send_email() helper
│   │   └── receipt_generator.py
│   ├── templates/              ← HTML email templates
│   ├── uploads/                ← User-uploaded files (not committed)
│   │   ├── event/
│   │   ├── payment_receipts/
│   │   ├── picture/
│   │   ├── presentation_templates/
│   │   └── abstract_presentations/
│   ├── alembic/                ← Database migrations
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env                    ← NOT committed — see §4
│   └── venv/                   ← NOT committed
│
├── web_vue/                    ← Active Vue 3 frontend (use this one)
│   ├── src/
│   │   ├── main.js             ← App bootstrap, Pinia, Router
│   │   ├── App.vue
│   │   ├── router/index.js     ← All routes (hash history)
│   │   ├── store/authStore.js  ← Pinia auth store
│   │   ├── services/
│   │   │   └── apiService.js   ← Axios instance + fetchData helpers
│   │   ├── layouts/            ← MainLayout, MyAccountLayout, WebLayout
│   │   ├── views/
│   │   │   ├── main/           ← Admin views (dashboard, events, abstracts…)
│   │   │   ├── my_account/     ← Normal user account views
│   │   │   └── web/            ← Public-facing pages
│   │   ├── components/         ← Reusable UI components
│   │   └── includes/           ← Header, Sidebar, Footer partials
│   ├── dist/                   ← Build output — NOT committed
│   ├── .env.development        ← Local API URL
│   ├── .env.production         ← Production API URL
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── web/                        ← Legacy frontend (archived — do not use)
├── setup_database.sql          ← Initial schema bootstrap
├── TEAM.md                     ← This file
└── README.md
```

> **Active frontend is `web_vue/`**. The `web/` directory is a legacy build kept for reference only — never deploy from it.

---

## 3. Local Development Setup

### Prerequisites

- macOS with XAMPP (or any local server running on port 80)
- Node.js ≥ 18, npm
- Python 3.11+ with `pip`
- Git
- SSH key for the production server (see §6)

### Clone the repository

```bash
git clone https://github.com/Davis1406/ecsaconm_events.git
cd ecsaconm_events
```

### Backend (FastAPI)

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create your local .env (copy from a team member — never commit this)
cp .env.example .env   # or ask lead for the file

# Run locally
uvicorn main:app --reload --port 8000
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Frontend (Vue 3)

```bash
cd web_vue
npm install

# Run dev server
npm run dev
# App available at http://localhost:5173
```

The `.env.development` file already points the frontend at the production API (`https://events.ecsaconm.org/api`). If you want to develop against a local API, change `VITE_API_URL` in that file to `http://localhost:8000`.

---

## 4. Environment Variables

### Backend — `api/.env`

| Variable | Description |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string — e.g. `mysql+mysqlconnector://user:pass@localhost/ecsaconm_events` |
| `SECRET_KEY` | JWT signing secret (keep this secret) |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes |
| `MAIL_USERNAME` | SMTP username |
| `MAIL_PASSWORD` | SMTP password |
| `MAIL_FROM` | Sender address |
| `MAIL_SERVER` | SMTP host |
| `MAIL_PORT` | SMTP port |
| `BASE_URL` | Public API base, e.g. `https://events.ecsaconm.org/api` |
| `CLIENT_ORIGIN` | Frontend origin, e.g. `https://events.ecsaconm.org` |

> **Never commit `.env`** — it contains secrets. Share securely with team members directly.

### Frontend — `web_vue/.env.production`

```
VITE_API_URL=https://events.ecsaconm.org/api
```

---

## 5. Version Control Workflow

### Repository

- **GitHub**: `https://github.com/Davis1406/ecsaconm_events`
- **Main branch**: `main` — this is what gets deployed to production

### Day-to-day workflow

```bash
# 1. Always start from a fresh main
git checkout main
git pull origin main

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes, then commit
git add .
git status          # review what's staged before committing
git commit -m "Short descriptive message"

# 4. Push and open a PR
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub targeting `main`. Get it reviewed before merging.

### Commit message conventions

- Use present tense: `Add email preview for template notifications`
- Prefix with the area: `Fix:`, `Add:`, `Update:`, `Remove:`
- Keep the first line under 72 characters

### What NOT to commit

The `.gitignore` covers these, but double-check:

```
api/venv/
api/.env
api/uploads/
web_vue/node_modules/
web_vue/dist/
web/node_modules/
web/dist/
**/__pycache__/
**/*.pyc
.DS_Store
```

---

## 6. Deployment

Deployments are **manual** — there is no CI/CD pipeline yet.

### Fast path — `deploy/deploy.sh`

The steps below are also wrapped in `deploy/deploy.sh` (and, in VS Code, as Run Task
entries prefixed `ecsaconm-deploy:`). It reads the same key/host as documented here
(override with `ECSACONM_DEPLOY_KEY` / `ECSACONM_DEPLOY_HOST` if yours differ), uses
`rsync` when installed and falls back to plain `tar`-over-`ssh` otherwise (nothing
extra to install), and refuses to run if the relevant directory (`api/` or
`web_vue/src/`) has uncommitted changes — commit and push first (Step 1 below), or
pass `--allow-dirty` for a genuine hotfix.

```bash
deploy/deploy.sh api --dry-run   # preview what would be synced
deploy/deploy.sh api             # sync api/, restart the ecsaconm service
deploy/deploy.sh web --dry-run   # preview the built dist/
deploy/deploy.sh web             # npm run build, then sync dist/
deploy/deploy.sh migrate         # alembic upgrade head on the server
deploy/deploy.sh status          # systemd status + recent logs
deploy/deploy.sh logs            # follow live API logs
```

The manual, step-by-step equivalent (useful if the script doesn't fit what you need,
or to understand what it's doing under the hood) follows.

### Prerequisites

You need the SSH private key for the EC2 server. Copy it to `/tmp` before starting:

```bash
cp ~/Downloads/keys/voting_ecsaconm/voting.pem /tmp/voting.pem
chmod 600 /tmp/voting.pem
```

> The key lives at `~/Downloads/keys/voting_ecsaconm/voting.pem`. Ask the project lead if you don't have it.

### Step 1 — Commit and push your changes

```bash
cd /path/to/ecsaconm_events
git add .
git commit -m "Your change description"
git push origin main
```

### Step 2 — Deploy the backend (if API files changed)

Only needed when you've changed anything inside `api/`.

```bash
scp -i /tmp/voting.pem \
  api/routers/your_changed_file.py \
  ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com:/var/www/ecsaconm_events/api/routers/your_changed_file.py
```

To deploy the **entire API** at once (e.g. after adding a new file or changing models):

```bash
rsync -az --exclude='venv' --exclude='.env' --exclude='uploads' \
  -e "ssh -i /tmp/voting.pem" \
  api/ \
  ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com:/var/www/ecsaconm_events/api/
```

Then restart the API service:

```bash
ssh -i /tmp/voting.pem ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com \
  "sudo systemctl restart ecsaconm && sudo systemctl is-active ecsaconm"
```

Expected output: `active`

### Step 3 — Deploy the frontend (if Vue files changed)

Only needed when you've changed anything inside `web_vue/src/`.

```bash
# 1. Build
cd web_vue
npm run build

# 2. Upload dist/ to server
rsync -az -e "ssh -i /tmp/voting.pem" \
  dist/ \
  ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com:/var/www/ecsaconm_events/web_vue/dist/
```

No service restart needed — Nginx serves the static files directly and picks up changes immediately.

### Step 4 — Verify

```bash
# Check API is running
ssh -i /tmp/voting.pem ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com \
  "sudo systemctl status ecsaconm --no-pager | tail -5"

# Check recent API logs for errors
ssh -i /tmp/voting.pem ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com \
  "sudo journalctl -u ecsaconm -n 30 --no-pager"
```

Then open **https://events.ecsaconm.org** in a browser and confirm the change works.

### Running database migrations

If you've added new models or changed existing columns, run Alembic on the server:

```bash
ssh -i /tmp/voting.pem ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com

# On the server:
cd /var/www/ecsaconm_events/api
source venv/bin/activate

# Generate a migration (if you changed models locally, generate locally first)
alembic revision --autogenerate -m "describe your change"

# Apply migrations
alembic upgrade head
```

> Always review the generated migration file before applying it — autogenerate can produce incorrect diffs.

---

## 7. Server Infrastructure

| Item | Value |
|---|---|
| **Provider** | AWS EC2 |
| **Instance** | `ec2-54-242-206-111.compute-1.amazonaws.com` |
| **OS** | Ubuntu |
| **SSH user** | `ubuntu` |
| **SSH key** | `~/Downloads/keys/voting_ecsaconm/voting.pem` |
| **Domain** | `events.ecsaconm.org` |
| **SSL** | Let's Encrypt via Certbot (auto-renewing) |

### Server paths

| What | Path |
|---|---|
| API source | `/var/www/ecsaconm_events/api/` |
| Frontend build | `/var/www/ecsaconm_events/web_vue/dist/` |
| Uploaded files | `/var/www/ecsaconm_events/api/uploads/` |
| Nginx config | `/etc/nginx/sites-enabled/ecsaconm` |
| Systemd service | `/etc/systemd/system/ecsaconm.service` |

### Nginx — how traffic flows

```
Browser → events.ecsaconm.org (HTTPS :443)
              │
              ├─ /api/*  → proxied to uvicorn at 127.0.0.1:8001
              ├─ /uploads/* → served directly from api/uploads/ (30d cache)
              └─ /*       → serves web_vue/dist/index.html (SPA fallback)
```

### Systemd service

The API runs as a systemd service named `ecsaconm`.

```bash
# Common service commands (run on server via SSH)
sudo systemctl status ecsaconm     # check status
sudo systemctl restart ecsaconm    # restart after API changes
sudo systemctl stop ecsaconm       # stop
sudo systemctl start ecsaconm      # start
sudo journalctl -u ecsaconm -f     # follow live logs
sudo journalctl -u ecsaconm -n 100 # last 100 log lines
```

Service config:
- **Runs as**: `ubuntu`
- **Working directory**: `/var/www/ecsaconm_events/api`
- **Command**: `uvicorn main:app --host 127.0.0.1 --port 8001 --workers 1`
- **Restarts**: automatically on crash (`Restart=always`)

---

## 8. Database

- **Engine**: MariaDB
- **Database name**: `ecsaconm_events`
- **ORM**: SQLAlchemy 2.0 (all models in `api/models/models.py`)
- **Migrations**: Alembic (`api/alembic/`)

### Key tables

| Table | Purpose |
|---|---|
| `user` | Auth accounts (email + hashed password) |
| `user_profile` | Profile details (title, gender, country, organisation) |
| `registration` | Event registrations (`paid` boolean, `participation_role`) |
| `event` | Conference events |
| `abstract` | Abstract submissions (`status`, `presentation_type`) |
| `presentation_template` | Admin-uploaded PPT/PDF templates |
| `abstract_presentation` | Presenter-uploaded filled presentations |
| `country` | Country lookup with `short_code` and `category` |
| `role` / `permission` / `role_permission` | RBAC |

### Direct database access (on server)

```bash
ssh -i /tmp/voting.pem ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com
sudo mysql -u root ecsaconm_events
```

---

## 9. Common Tasks

### Add a new API route

1. Add the endpoint function in the appropriate `api/routers/*.py` file.
2. **Important**: if your route has a literal path (e.g. `/my-route`), place it **before** any parameterised routes (`/{id}`) in the same file — FastAPI matches top-to-bottom and a wildcard will catch your literal path first.
3. If it's an entirely new resource, create `api/routers/new_resource.py` and register it in `api/main.py`.
4. Deploy only the changed router file (Step 2 above) and restart the service.

### Add a new frontend page

1. Create `web_vue/src/views/.../YourPage.vue` using **Options API** (no `<script setup>`, no `ref()`).
2. Add a lazy route in `web_vue/src/router/index.js`:
   ```js
   YourPageView: () => import("@/views/.../YourPage.vue")
   ```
3. Add the route entry under the correct layout's `children` array.
4. If it belongs in the My Account sidebar, add a `<router-link>` in `MyAccountLayout.vue`.

### Check production logs for errors

```bash
ssh -i /tmp/voting.pem ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com \
  "sudo journalctl -u ecsaconm --since '1 hour ago' --no-pager | grep -i error"
```

### Renew SSL certificate (if it ever expires)

```bash
ssh -i /tmp/voting.pem ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com
sudo certbot renew --dry-run   # test first
sudo certbot renew             # actually renew
sudo systemctl reload nginx
```

Certbot sets up a cron job that auto-renews, so this should rarely be needed manually.

### Install a new Python package

```bash
# Locally
cd api && source venv/bin/activate
pip install package-name
pip freeze > requirements.txt

# On server
ssh -i /tmp/voting.pem ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com
cd /var/www/ecsaconm_events/api
source venv/bin/activate
pip install package-name
sudo systemctl restart ecsaconm
```

---

## 10. Coding Conventions

### Backend (Python / FastAPI)

- One router file per resource group; register all in `main.py`.
- Literal route paths must always be declared **before** parameterised routes in the same router — FastAPI resolves top-to-bottom.
- Use `joinedload()` for related models to avoid N+1 queries.
- Permission checks via `auth.secure_access("PERMISSION_CODE", user_id)` — admin bypass uses `ADMIN_DASHBOARD`.
- Email sending goes through `background_tasks.add_task(send_email, ...)` — never block the request.

### Frontend (Vue 3)

- **Options API only** — no `<script setup>`, no `ref()`, no `reactive()`.
- Brand colours: Primary `rgb(254, 80, 103)` · Secondary `rgb(220, 50, 75)`. Never use teal, orange, or black as accents.
- Axios calls go through `this._api()` (creates an instance with the current auth token) or through `apiService.fetchData()` which uses a request interceptor — never construct raw axios calls with hardcoded headers.
- Pinia auth store: `useAuthStore()` → fields `loginUser`, `accessToken`, `permissions`.
- Routes use hash history (`createWebHashHistory`) — all URLs are `/#/path`.
- Check `this.authStore.permissions` and the `ADMIN_DASHBOARD` permission code for admin-only UI.

---

*Last updated: August 2026 · Maintained by the ECSACONM development team*
