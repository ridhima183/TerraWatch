from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Integer, String, Float, DateTime

from database import Base


# =========================================================
# CITY DATABASE MODEL
# =========================================================

class City(Base):
    __tablename__ = "cities"

    city_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    city_name = Column(
        String,
        nullable=False
    )

    state = Column(
        String,
        nullable=False
    )

    country = Column(
        String,
        nullable=False
    )

    temperature = Column(
        Float,
        nullable=False
    )

    humidity = Column(
        Float,
        nullable=False
    )

    weather_condition = Column(
        String,
        nullable=False
    )

    # Automatically obtained from Open-Meteo
    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    recorded_at = Column(
        DateTime,
        nullable=False
    )


# =========================================================
# DISASTER DATABASE MODEL
# =========================================================

class Disaster(Base):
    __tablename__ = "disasters"

    disaster_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    region_name = Column(
        String,
        nullable=False
    )

    state = Column(
        String,
        nullable=False
    )

    country = Column(
        String,
        nullable=False
    )

    disaster_type = Column(
        String,
        nullable=False
    )

    severity = Column(
        String,
        nullable=False
    )

    affected_population = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    # Automatically obtained from Open-Meteo
    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    recorded_at = Column(
        DateTime,
        nullable=False
    )


# =========================================================
# CITY CREATE
# =========================================================

class CityCreate(BaseModel):

    city_name: str = Field(min_length=1)
    state: str = Field(min_length=1)
    country: str = Field(min_length=1)

    temperature: float

    humidity: float = Field(
        ge=0,
        le=100
    )

    weather_condition: str = Field(
        min_length=1
    )


# =========================================================
# CITY UPDATE
# =========================================================

class CityUpdate(BaseModel):

    city_name: str = Field(min_length=1)
    state: str = Field(min_length=1)
    country: str = Field(min_length=1)

    temperature: float

    humidity: float = Field(
        ge=0,
        le=100
    )

    weather_condition: str = Field(
        min_length=1
    )


# =========================================================
# CITY RESPONSE
# =========================================================

class CityResponse(BaseModel):

    city_id: int
    city_name: str
    state: str
    country: str
    temperature: float
    humidity: float
    weather_condition: str

    latitude: float | None = None
    longitude: float | None = None

    recorded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# WEATHER REQUEST
# =========================================================

class WeatherRequest(BaseModel):

    city_name: str = Field(
        min_length=1
    )


# =========================================================
# DISASTER CREATE
# =========================================================

class DisasterCreate(BaseModel):

    region_name: str = Field(
        min_length=1
    )

    state: str = Field(
        min_length=1
    )

    country: str = Field(
        min_length=1
    )

    disaster_type: str = Field(
        min_length=1
    )

    severity: str = Field(
        min_length=1
    )

    affected_population: int = Field(
        ge=0
    )

    status: str = Field(
        min_length=1
    )

    description: str = Field(
        min_length=1
    )


# =========================================================
# DISASTER UPDATE
# =========================================================

class DisasterUpdate(BaseModel):

    region_name: str = Field(
        min_length=1
    )

    state: str = Field(
        min_length=1
    )

    country: str = Field(
        min_length=1
    )

    disaster_type: str = Field(
        min_length=1
    )

    severity: str = Field(
        min_length=1
    )

    affected_population: int = Field(
        ge=0
    )

    status: str = Field(
        min_length=1
    )

    description: str = Field(
        min_length=1
    )


# =========================================================
# DISASTER RESPONSE
# =========================================================

class DisasterResponse(BaseModel):

    disaster_id: int
    region_name: str
    state: str
    country: str
    disaster_type: str
    severity: str
    affected_population: int
    status: str
    description: str

    latitude: float | None = None
    longitude: float | None = None

    recorded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )