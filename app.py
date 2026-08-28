from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.enquiries import router as enquiries_router
from routes.destinations import router as destinations_router
from routes.experiences import router as experiences_router
from routes.admin import router as admin_router
from routes.planner import router as planner_router

from database.database import init_db


app = FastAPI(
    title="TravelVibe API",
    version="3.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# DATABASE
# =========================================================

init_db()


# =========================================================
# API ROUTES
# =========================================================

app.include_router(
    enquiries_router,
    prefix="/api"
)

app.include_router(
    destinations_router,
    prefix="/api"
)

app.include_router(
    experiences_router,
    prefix="/api"
)

app.include_router(
    admin_router,
    prefix="/api"
)

# TravelVibe AI Planner
app.include_router(
    planner_router,
    prefix="/api"
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "app": "TravelVibe API",
        "status": "running",
        "version": "3.0.0"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }
