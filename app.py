from fastapi import FastAPI

from database import engine, Base

from routes.city_routes import router as city_router
from routes.disaster_routes import router as disaster_router

import models


app = FastAPI(
    title="City & Disaster Information API",
    description=(
        "REST API for city weather information "
        "and regional disaster management."
    ),
    version="1.0.0"
)


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# REGISTER ROUTERS
# =========================================================

app.include_router(city_router)

app.include_router(disaster_router)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": (
            "City & Disaster Information API is running"
        )
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "UP"
    }