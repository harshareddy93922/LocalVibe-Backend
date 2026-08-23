from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.enquiries import router as enquiries_router
from routes.destinations import router as destinations_router
from routes.experiences import router as experiences_router
from routes.admin import router as admin_router
from database.database import init_db

app = FastAPI(title="LocalVibe API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(enquiries_router, prefix="/api")
app.include_router(destinations_router, prefix="/api")
app.include_router(experiences_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

@app.get("/")
def root():
    return {"app": "LocalVibe API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}
