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

# ✅ Read frontend URL from environment (Render)
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"  # fallback for local development
)

# ✅ CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],   # only allow your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])

# ✅ Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# ✅ Root endpoint
@app.get("/")
def root():
    return {"message": "API is running 🚀"}