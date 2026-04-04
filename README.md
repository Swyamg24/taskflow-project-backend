# TaskFlow RBAC — Backend

A production-ready REST API built with **FastAPI** and **PostgreSQL**, featuring JWT authentication and role-based access control (RBAC). Users can register, log in, and manage their own tasks. Admins have full visibility and control over all users and tasks.

**Live API:** https://taskflow-project-backend-w2in.onrender.com  
**Swagger Docs:** https://taskflow-project-backend-w2in.onrender.com/docs

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.135+ |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT via `python-jose` |
| Password hashing | `bcrypt` via `passlib` |
| Validation | Pydantic v2 |
| Server | Uvicorn |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # App entry point, CORS config, router registration
│   ├── database.py          # SQLAlchemy engine, session factory, get_db dependency
│   ├── models.py            # User and Task SQLAlchemy models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth/
│   │   ├── dependencies.py  # get_current_user, require_admin FastAPI dependencies
│   │   ├── hashing.py       # bcrypt password hash/verify helpers
│   │   └── jwt.py           # JWT create and verify functions
│   ├── crud/
│   │   ├── user_crud.py     # DB operations for users
│   │   └── task_crud.py     # DB operations for tasks
│   └── routers/
│       ├── auth.py          # /api/v1/auth routes
│       └── tasks.py         # /api/v1/tasks routes
├── .env                     # Local environment variables (never commit this)
├── .env.example             # Template for required env vars
└── requirements.txt
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL running locally **or** a Supabase project

### Steps

```bash
# 1. Clone and enter the directory
git clone <your-repo-url>
cd backend

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# Fill in the values (see Environment Variables section below)

# 5. Create the PostgreSQL database (skip if using Supabase)
psql -U postgres -c "CREATE DATABASE taskflow;"

# 6. Start the development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

---

## Environment Variables

Create a `.env` file in the `backend/` root with these keys:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:3000
```

### For Supabase (Transaction Pooler)
Use the **Transaction Pooler** connection string from your Supabase project dashboard and append `?sslmode=require`:

```env
DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require
```

> **Never commit `.env` to version control.** Add it to `.gitignore`.

---

## API Endpoints

### Auth — `/api/v1/auth`

| Method | Path | Auth Required | Role | Description |
|--------|------|:---:|:---:|---|
| `POST` | `/register` | ✗ | Any | Create a new user account |
| `POST` | `/login` | ✗ | Any | Login and receive a JWT token |
| `GET` | `/me` | ✓ | Any | Get the current logged-in user's profile |
| `GET` | `/users` | ✓ | Admin only | List all registered users |

### Tasks — `/api/v1/tasks`

| Method | Path | Auth Required | Role | Description |
|--------|------|:---:|:---:|---|
| `GET` | `/` | ✓ | Any | Get tasks (users see own; admins see all) |
| `POST` | `/` | ✓ | Any | Create a new task |
| `GET` | `/{id}` | ✓ | Owner / Admin | Get a specific task |
| `PUT` | `/{id}` | ✓ | Owner / Admin | Update a task |
| `DELETE` | `/{id}` | ✓ | Owner / Admin | Delete a task |

### Authentication

All protected routes require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Request & Response Examples

### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "secret123"
}
```
```json
// 201 Created
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "user",
  "created_at": "2026-04-04T10:00:00Z"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "jane@example.com",
  "password": "secret123"
}
```
```json
// 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "user",
    "created_at": "2026-04-04T10:00:00Z"
  }
}
```

### Create Task
```http
POST /api/v1/tasks/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Write unit tests",
  "description": "Cover auth and task endpoints"
}
```
```json
// 201 Created
{
  "id": 1,
  "title": "Write unit tests",
  "description": "Cover auth and task endpoints",
  "status": "pending",
  "owner_id": 1,
  "created_at": "2026-04-04T10:05:00Z",
  "updated_at": null
}
```

---

## Data Models

### User
| Field | Type | Notes |
|---|---|---|
| `id` | integer | Primary key |
| `name` | string(100) | Required |
| `email` | string(150) | Unique, indexed |
| `hashed_password` | string(255) | Never returned in responses |
| `role` | string | `"user"` (default) or `"admin"` |
| `is_active` | boolean | Default `true` |
| `created_at` | datetime | Auto-set by DB |

### Task
| Field | Type | Notes |
|---|---|---|
| `id` | integer | Primary key |
| `title` | string(255) | Required |
| `description` | text | Optional |
| `status` | string | `pending` / `in_progress` / `done` |
| `owner_id` | integer | Foreign key → User |
| `created_at` | datetime | Auto-set by DB |
| `updated_at` | datetime | Auto-updated on change |

---

## Deployment (Render)

1. Push your code to GitHub.
2. Create a new **Web Service** on [Render](https://render.com), connect your repo.
3. Set the following in Render → **Environment**:

| Key | Value |
|---|---|
| `DATABASE_URL` | Your Supabase connection string + `?sslmode=require` |
| `SECRET_KEY` | A long random string |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `FRONTEND_URL` | Your Vercel frontend URL |
| `PYTHON_VERSION` | `3.11.0` |

4. Set the **Start Command** to:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

> Do not use `--reload` in production and do not hardcode `--port 8000` — Render assigns the port dynamically via `$PORT`.

---

## CORS

The following origins are whitelisted by default. Add more via the `CORS_ORIGINS` environment variable (comma-separated):

```env
CORS_ORIGINS=https://your-preview.vercel.app,https://staging.example.com
```

---

## Scalability Notes

- **Stateless JWT** — any server instance can verify any token; horizontally scalable with no shared session state.
- **SQLAlchemy connection pool** — efficiently handles concurrent DB access.
- **Pydantic validation** — bad data is rejected before it reaches business logic or the database.
- **Modular routers** — new feature areas (e.g. comments, projects) can be added without touching existing code.

**Suggested next steps:** Alembic for DB migrations, Docker + docker-compose, Redis caching, Nginx load balancer.