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
env_frontend = os.getenv("FRONTEND_URL")

# ✅ Define explicitly allowed origins to ensure it works in both dev and prod
# We include your exact Vercel URL as a hardcoded failsafe just in case 
# the Render environment variable isn't set up perfectly yet.
origins = [
    "https://taskflow-project-frontend-one.vercel.app",  # Production Failsafe
    "http://localhost:3000",                             # Local React Failsafe
    "http://localhost:5173",                             # Local Vite Failsafe
]

# If the env variable exists and isn't already in the list, add it.
# (We strip any accidental trailing slashes to prevent CORS failures)
if env_frontend:
    clean_env_url = env_frontend.rstrip("/")
    if clean_env_url not in origins:
        origins.append(clean_env_url)

# ✅ CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows any URL listed in the origins array above
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