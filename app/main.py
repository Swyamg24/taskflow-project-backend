from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app import models
from app.routers import auth, tasks

# Auto-create tables from SQLAlchemy models (dev convenience)
# In production, use Alembic migrations instead
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intern Project API",
    description="REST API with JWT Auth & Role-Based Access",
    version="1.0.0",
    # Swagger UI → http://localhost:8000/docs
    # ReDoc      → http://localhost:8000/redoc
)

# ── CORS Middleware ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ─────────────────────────────────────────
app.include_router(auth.router)
app.include_router(tasks.router)

# ── Health Check ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/")
def root():
    return {"message": "API is running 🚀"}