from fastapi import FastAPI
from app.routers import auth, doctors, appointments
from app.database import engine, Base

app = FastAPI(
    title="Doctor Appointment API",
    description="Production-ready RESTful API for managing doctor appointments",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(appointments.router)


@app.on_event("startup")
async def startup():
   
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {
        "message": "Doctor Appointment API",
        "version": "1.0.0",
        "docs": "/docs"
    }

