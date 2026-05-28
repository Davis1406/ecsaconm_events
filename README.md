# ECSACONM Events — Local Development Setup

## Project Structure
```
ecsaconm_events/
  api/    — FastAPI backend (port 8001)
  web/    — Vue 3 + Vite frontend (port 5174)
```

## 1. Start MySQL (XAMPP)
Open the XAMPP Manager app and start MySQL. Or run:
```bash
sudo /Applications/XAMPP/xamppfiles/bin/mysql.server start
```

## 2. Create Database
```bash
/Applications/XAMPP/xamppfiles/bin/mysql -u root < setup_database.sql
```

## 3. Run Database Migrations
```bash
cd api
source venv/bin/activate
alembic upgrade head
```

## 4. Seed Initial Data (optional)
```bash
cd api
source venv/bin/activate
python seed_roles.py
python seed_permissions.py
```

## 5. Start the API
```bash
cd api
source venv/bin/activate
uvicorn main:app --reload --port 8001
```
API docs available at: http://localhost:8001/docs

## 6. Start the Frontend
```bash
cd web
npm run dev -- --port 5174
```
App available at: http://localhost:5174

## Environment
- API `.env` — database: `ecsaconm_events`, port `8001`
- Web `.env.development` — API URL: `http://localhost:8001`
