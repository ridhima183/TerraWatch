# =========================================================
# CITY VALIDATION
# =========================================================

def validate_city_data(
    city_name: str,
    state: str,
    country: str,
    weather_condition: str
):

    errors = []

    if not city_name.strip():
        errors.append(
            "city_name cannot be empty"
        )

    if not state.strip():
        errors.append(
            "state cannot be empty"
        )

    if not country.strip():
        errors.append(
            "country cannot be empty"
        )

    if not weather_condition.strip():
        errors.append(
            "weather_condition cannot be empty"
        )

    return errors


# =========================================================
# DISASTER VALIDATION
# =========================================================

VALID_DISASTER_TYPES = {
    "Flood",
    "Cyclone",
    "Earthquake",
    "Landslide",
    "Drought",
    "Wildfire",
    "Tsunami",
    "Heatwave",
    "Other"
}


VALID_SEVERITIES = {
    "Low",
    "Medium",
    "High",
    "Critical"
}


VALID_STATUSES = {
    "Active",
    "Monitoring",
    "Resolved"
}


def validate_disaster_data(disaster):

    errors = {}

    if not disaster.region_name.strip():
        errors["region_name"] = (
            "Region name must not be empty."
        )

    if not disaster.state.strip():
        errors["state"] = (
            "State must not be empty."
        )

    if not disaster.country.strip():
        errors["country"] = (
            "Country must not be empty."
        )

    if not disaster.disaster_type.strip():
        errors["disaster_type"] = (
            "Disaster type must not be empty."
        )

    elif disaster.disaster_type not in VALID_DISASTER_TYPES:
        errors["disaster_type"] = (
            "Invalid disaster type. "
            "Allowed values: "
            + ", ".join(
                sorted(VALID_DISASTER_TYPES)
            )
        )

    if not disaster.severity.strip():
        errors["severity"] = (
            "Severity must not be empty."
        )

    elif disaster.severity not in VALID_SEVERITIES:
        errors["severity"] = (
            "Invalid severity. "
            "Allowed values: "
            + ", ".join(
                sorted(VALID_SEVERITIES)
            )
        )

    if disaster.affected_population < 0:
        errors["affected_population"] = (
            "Affected population cannot be negative."
        )

    if not disaster.status.strip():
        errors["status"] = (
            "Status must not be empty."
        )

    elif disaster.status not in VALID_STATUSES:
        errors["status"] = (
            "Invalid status. "
            "Allowed values: "
            + ", ".join(
                sorted(VALID_STATUSES)
            )
        )

    if not disaster.description.strip():
        errors["description"] = (
            "Description must not be empty."
        )

    return errors if errors else None