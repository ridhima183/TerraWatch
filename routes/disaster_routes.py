from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Disaster,
    DisasterCreate,
    DisasterUpdate,
    DisasterResponse
)

from validators import validate_disaster_data

from weather_service import get_coordinates


router = APIRouter(
    prefix="/disasters",
    tags=["Disasters"]
)


# =========================================================
# GET ALL DISASTERS + FILTERING
# =========================================================

@router.get(
    "",
    response_model=list[DisasterResponse]
)
def get_disasters(
    state: str | None = None,
    disaster_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(Disaster)

    if state:

        query = query.filter(
            Disaster.state.ilike(state)
        )

    if disaster_type:

        query = query.filter(
            Disaster.disaster_type == disaster_type
        )

    if severity:

        query = query.filter(
            Disaster.severity == severity
        )

    if status:

        query = query.filter(
            Disaster.status == status
        )

    disasters = query.all()

    # -----------------------------------------------------
    # BACKFILL OLD DISASTER COORDINATES
    # -----------------------------------------------------

    changed = False

    for disaster in disasters:

        if (
            disaster.latitude is None
            or disaster.longitude is None
        ):

            try:

                location = get_coordinates(
                    disaster.region_name,
                    disaster.state,
                    disaster.country
                )

                disaster.latitude = (
                    location["latitude"]
                )

                disaster.longitude = (
                    location["longitude"]
                )

                changed = True

            except Exception:
                continue

    if changed:

        db.commit()

    return disasters


# =========================================================
# DISASTER STATISTICS
# =========================================================

@router.get(
    "/statistics/summary"
)
def get_disaster_statistics(
    db: Session = Depends(get_db)
):

    disasters = db.query(Disaster).all()

    total_disasters = len(disasters)

    active_disasters = sum(
        1
        for disaster in disasters
        if disaster.status == "Active"
    )

    high_severity_disasters = sum(
        1
        for disaster in disasters
        if disaster.severity in {
            "High",
            "Critical"
        }
    )

    total_affected_population = sum(
        disaster.affected_population
        for disaster in disasters
    )

    return {
        "total_disasters": total_disasters,

        "active_disasters": active_disasters,

        "high_severity_disasters": (
            high_severity_disasters
        ),

        "total_affected_population": (
            total_affected_population
        )
    }


# =========================================================
# GET DISASTER BY ID
# =========================================================

@router.get(
    "/{disaster_id}",
    response_model=DisasterResponse
)
def get_disaster(
    disaster_id: int,
    db: Session = Depends(get_db)
):

    disaster = db.query(Disaster).filter(
        Disaster.disaster_id == disaster_id
    ).first()

    if disaster is None:

        raise HTTPException(
            status_code=404,
            detail="Disaster not found."
        )

    # Automatically obtain coordinates
    if (
        disaster.latitude is None
        or disaster.longitude is None
    ):

        try:

            location = get_coordinates(
                disaster.region_name,
                disaster.state,
                disaster.country
            )

            disaster.latitude = (
                location["latitude"]
            )

            disaster.longitude = (
                location["longitude"]
            )

            db.commit()
            db.refresh(disaster)

        except Exception:
            pass

    return disaster


# =========================================================
# CREATE DISASTER
# =========================================================

@router.post(
    "",
    response_model=DisasterResponse,
    status_code=201
)
def create_disaster(
    disaster: DisasterCreate,
    db: Session = Depends(get_db)
):

    validation_errors = validate_disaster_data(
        disaster
    )

    if validation_errors:

        raise HTTPException(
            status_code=400,
            detail=validation_errors
        )

    # -----------------------------------------------------
    # AUTOMATIC GEOCODING
    # -----------------------------------------------------

    try:

        location = get_coordinates(
            disaster.region_name,
            disaster.state,
            disaster.country
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

    new_disaster = Disaster(

        region_name=(
            disaster.region_name.strip()
        ),

        state=(
            disaster.state.strip()
        ),

        country=(
            disaster.country.strip()
        ),

        disaster_type=(
            disaster.disaster_type.strip()
        ),

        severity=(
            disaster.severity.strip()
        ),

        affected_population=(
            disaster.affected_population
        ),

        status=(
            disaster.status.strip()
        ),

        description=(
            disaster.description.strip()
        ),

        latitude=location["latitude"],

        longitude=location["longitude"],

        recorded_at=datetime.now()
    )

    db.add(new_disaster)

    db.commit()

    db.refresh(new_disaster)

    return new_disaster


# =========================================================
# UPDATE DISASTER
# =========================================================

@router.put(
    "/{disaster_id}",
    response_model=DisasterResponse
)
def update_disaster(
    disaster_id: int,
    disaster: DisasterUpdate,
    db: Session = Depends(get_db)
):

    existing_disaster = db.query(
        Disaster
    ).filter(
        Disaster.disaster_id == disaster_id
    ).first()

    if existing_disaster is None:

        raise HTTPException(
            status_code=404,
            detail="Disaster not found."
        )

    validation_errors = validate_disaster_data(
        disaster
    )

    if validation_errors:

        raise HTTPException(
            status_code=400,
            detail=validation_errors
        )

    # -----------------------------------------------------
    # AUTOMATICALLY RE-CALCULATE COORDINATES
    # -----------------------------------------------------

    try:

        location = get_coordinates(
            disaster.region_name,
            disaster.state,
            disaster.country
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

    existing_disaster.region_name = (
        disaster.region_name.strip()
    )

    existing_disaster.state = (
        disaster.state.strip()
    )

    existing_disaster.country = (
        disaster.country.strip()
    )

    existing_disaster.disaster_type = (
        disaster.disaster_type.strip()
    )

    existing_disaster.severity = (
        disaster.severity.strip()
    )

    existing_disaster.affected_population = (
        disaster.affected_population
    )

    existing_disaster.status = (
        disaster.status.strip()
    )

    existing_disaster.description = (
        disaster.description.strip()
    )

    existing_disaster.latitude = (
        location["latitude"]
    )

    existing_disaster.longitude = (
        location["longitude"]
    )

    existing_disaster.recorded_at = datetime.now()

    db.commit()

    db.refresh(existing_disaster)

    return existing_disaster


# =========================================================
# DELETE DISASTER
# =========================================================

@router.delete(
    "/{disaster_id}"
)
def delete_disaster(
    disaster_id: int,
    db: Session = Depends(get_db)
):

    disaster = db.query(Disaster).filter(
        Disaster.disaster_id == disaster_id
    ).first()

    if disaster is None:

        raise HTTPException(
            status_code=404,
            detail="Disaster not found."
        )

    db.delete(disaster)

    db.commit()

    return {
        "message": "Disaster deleted successfully.",
        "disaster_id": disaster_id
    }