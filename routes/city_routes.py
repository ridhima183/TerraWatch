from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    City,
    CityCreate,
    CityUpdate,
    CityResponse,
    WeatherRequest
)

from validators import validate_city_data

from weather_service import get_weather, get_coordinates


router = APIRouter(
    prefix="/cities",
    tags=["Cities & Weather"]
)


# =========================================================
# CREATE CITY
# =========================================================

@router.post(
    "",
    response_model=CityResponse,
    status_code=201
)
def create_city(
    city: CityCreate,
    db: Session = Depends(get_db)
):

    errors = validate_city_data(
        city.city_name,
        city.state,
        city.country,
        city.weather_condition
    )

    if errors:
        raise HTTPException(
            status_code=400,
            detail=errors
        )

    # -----------------------------------------------------
    # AUTOMATIC GEOCODING
    # -----------------------------------------------------

    try:

        location = get_coordinates(
            city.city_name,
            city.state,
            city.country
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Location service unavailable"
        )

    # -----------------------------------------------------
    # CREATE RECORD
    # -----------------------------------------------------

    new_city = City(

        city_name=city.city_name.strip(),

        state=city.state.strip(),

        country=city.country.strip(),

        temperature=city.temperature,

        humidity=city.humidity,

        weather_condition=(
            city.weather_condition.strip()
        ),

        latitude=location["latitude"],

        longitude=location["longitude"],

        recorded_at=datetime.now()
    )

    db.add(new_city)

    db.commit()

    db.refresh(new_city)

    return new_city


# =========================================================
# CREATE CITY FROM LIVE WEATHER
# =========================================================

@router.post(
    "/weather",
    response_model=CityResponse,
    status_code=201
)
def create_city_from_weather(
    request: WeatherRequest,
    db: Session = Depends(get_db)
):

    try:

        weather = get_weather(
            request.city_name
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Weather service unavailable"
        )

    new_city = City(

        city_name=weather["city_name"],

        state=weather["state"] or "Unknown",

        country=weather["country"],

        temperature=weather["temperature"],

        humidity=weather["humidity"],

        weather_condition=(
            weather["weather_condition"]
        ),

        latitude=weather["latitude"],

        longitude=weather["longitude"],

        recorded_at=datetime.fromisoformat(
            weather["recorded_at"]
        )
    )

    db.add(new_city)

    db.commit()

    db.refresh(new_city)

    return new_city


# =========================================================
# GET CITIES + FILTERING
# =========================================================

@router.get(
    "",
    response_model=list[CityResponse]
)
def get_cities(
    state: str | None = None,

    min_temperature: float | None = Query(
        default=None
    ),

    db: Session = Depends(get_db)
):

    query = db.query(City)

    if state:

        query = query.filter(
            City.state.ilike(state)
        )

    if min_temperature is not None:

        query = query.filter(
            City.temperature >= min_temperature
        )

    cities = query.all()

    # -----------------------------------------------------
    # BACKFILL COORDINATES FOR OLD RECORDS
    # -----------------------------------------------------

    changed = False

    for city in cities:

        if (
            city.latitude is None
            or city.longitude is None
        ):

            try:

                location = get_coordinates(
                    city.city_name,
                    city.state,
                    city.country
                )

                city.latitude = (
                    location["latitude"]
                )

                city.longitude = (
                    location["longitude"]
                )

                changed = True

            except Exception:
                # Don't break GET /cities if
                # one location cannot be geocoded.
                continue

    if changed:

        db.commit()

    return cities


# =========================================================
# CITY STATISTICS
# =========================================================

@router.get(
    "/statistics"
)
def get_city_statistics(
    db: Session = Depends(get_db)
):

    cities = db.query(City).all()

    if not cities:

        return {
            "total_cities": 0,
            "average_temperature": 0,
            "maximum_temperature": None,
            "minimum_temperature": None
        }

    temperatures = [
        city.temperature
        for city in cities
    ]

    return {
        "total_cities": len(cities),

        "average_temperature": round(
            sum(temperatures) / len(temperatures),
            2
        ),

        "maximum_temperature": max(
            temperatures
        ),

        "minimum_temperature": min(
            temperatures
        )
    }


# =========================================================
# GET CITY BY ID
# =========================================================

@router.get(
    "/{city_id}",
    response_model=CityResponse
)
def get_city(
    city_id: int,
    db: Session = Depends(get_db)
):

    city = db.query(City).filter(
        City.city_id == city_id
    ).first()

    if city is None:

        raise HTTPException(
            status_code=404,
            detail="City not found"
        )

    # Automatically fill coordinates
    if (
        city.latitude is None
        or city.longitude is None
    ):

        try:

            location = get_coordinates(
                city.city_name,
                city.state,
                city.country
            )

            city.latitude = location["latitude"]
            city.longitude = location["longitude"]

            db.commit()
            db.refresh(city)

        except Exception:
            pass

    return city


# =========================================================
# UPDATE CITY
# =========================================================

@router.put(
    "/{city_id}",
    response_model=CityResponse
)
def update_city(
    city_id: int,
    city_data: CityUpdate,
    db: Session = Depends(get_db)
):

    city = db.query(City).filter(
        City.city_id == city_id
    ).first()

    if city is None:

        raise HTTPException(
            status_code=404,
            detail="City not found"
        )

    errors = validate_city_data(
        city_data.city_name,
        city_data.state,
        city_data.country,
        city_data.weather_condition
    )

    if errors:

        raise HTTPException(
            status_code=400,
            detail=errors
        )

    # -----------------------------------------------------
    # AUTOMATICALLY RE-CALCULATE COORDINATES
    # -----------------------------------------------------

    try:

        location = get_coordinates(
            city_data.city_name,
            city_data.state,
            city_data.country
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Location service unavailable"
        )

    city.city_name = (
        city_data.city_name.strip()
    )

    city.state = (
        city_data.state.strip()
    )

    city.country = (
        city_data.country.strip()
    )

    city.temperature = (
        city_data.temperature
    )

    city.humidity = (
        city_data.humidity
    )

    city.weather_condition = (
        city_data.weather_condition.strip()
    )

    city.latitude = location["latitude"]

    city.longitude = location["longitude"]

    city.recorded_at = datetime.now()

    db.commit()

    db.refresh(city)

    return city


# =========================================================
# DELETE CITY
# =========================================================

@router.delete(
    "/{city_id}"
)
def delete_city(
    city_id: int,
    db: Session = Depends(get_db)
):

    city = db.query(City).filter(
        City.city_id == city_id
    ).first()

    if city is None:

        raise HTTPException(
            status_code=404,
            detail="City not found"
        )

    db.delete(city)

    db.commit()

    return {
        "message": "City deleted successfully",
        "city_id": city_id
    }