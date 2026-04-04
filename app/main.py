import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app import models
from app.routers import auth, tasks

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Backend Project API",
    version="1.0.0",
)

# ── CORS ORIGINS ──────────────────────────────────────────────────────────────
# FIX: Added 127.0.0.1 variants — browsers sometimes send 127.0.0.1 instead of
# localhost, which caused the origin check to fail and blocked all requests.
# FIX: Support CORS_ORIGINS env var as a comma-separated list of extra URLs
# so you can add any custom domain without hardcoding.

origins = [
    # Production
    "https://taskflow-project-frontend-one.vercel.app",

    # Local dev — both "localhost" and "127.0.0.1" variants are required
    # because different browsers/OS may use either form as the Origin header.
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Single extra URL from env (backward-compatible with existing Render config)
env_frontend = os.getenv("FRONTEND_URL")
if env_frontend:
    clean = env_frontend.rstrip("/")
    if clean not in origins:
        origins.append(clean)

# NEW: comma-separated list of extra origins, e.g. for staging/preview URLs
# Set CORS_ORIGINS="https://my-preview.vercel.app,https://staging.example.com"
extra_origins = os.getenv("CORS_ORIGINS", "")
for url in extra_origins.split(","):
    url = url.strip().rstrip("/")
    if url and url not in origins:
        origins.append(url)

# ── CORS MIDDLEWARE ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTERS ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])

# ── UTILITY ENDPOINTS ─────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "API is running 🚀"}