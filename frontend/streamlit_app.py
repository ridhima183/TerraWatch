import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="TerraWatch",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0d1016;
        color: #f5f7fa;
    }

    section[data-testid="stSidebar"] {
        background-color: #24262f;
    }

    section[data-testid="stSidebar"] * {
        color: #f5f7fa;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(
            120deg,
            #101c32,
            #145b6d
        );
        padding: 38px 42px;
        border-radius: 0 0 24px 24px;
        margin-bottom: 30px;
    }

    .hero-small {
        font-size: 0.85rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #cbd5e1;
        opacity: 0.8;
        margin-bottom: 10px;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 750;
        color: white;
        margin-bottom: 10px;
    }

    .hero-text {
        font-size: 1.1rem;
        color: #dbeafe;
        opacity: 0.9;
        max-width: 750px;
        line-height: 1.6;
    }

    .metric-card {
        background: #171a22;
        border: 1px solid #292e39;
        border-radius: 16px;
        padding: 22px;
        min-height: 120px;
    }

    .metric-title {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 700;
    }

    .alert-card {
        background: #171a22;
        border-left: 5px solid #f87171;
        border-radius: 15px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }

    .alert-title {
        color: #f8fafc;
        font-size: 1.05rem;
        font-weight: 700;
    }

    .alert-location {
        color: #cbd5e1;
        margin-top: 7px;
    }

    .alert-details {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 8px;
    }

    .weather-card {
        background: linear-gradient(
            145deg,
            #172033,
            #123b4a
        );
        border-radius: 18px;
        padding: 25px;
        color: white;
    }

    .weather-location {
        font-size: 1.3rem;
        font-weight: 700;
    }

    .weather-temp {
        font-size: 2.8rem;
        font-weight: 750;
        margin-top: 10px;
    }

    .weather-condition {
        color: #cbd5e1;
        margin-top: 5px;
    }

    .weather-humidity {
        color: #94a3b8;
        margin-top: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# API FUNCTIONS
# ============================================================

def api_get(endpoint, params=None):

    try:

        response = requests.get(
            f"{API_URL}{endpoint}",
            params=params,
            timeout=15
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:

        return None


def api_request(
    method,
    endpoint,
    data=None,
    params=None
):

    try:

        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            json=data,
            params=params,
            timeout=15
        )

        return response

    except requests.exceptions.RequestException as e:

        st.error(
            f"API connection error: {e}"
        )

        return None


def show_api_error(
    response,
    default_message
):

    try:

        data = response.json()

        st.error(
            data.get(
                "detail",
                default_message
            )
        )

    except Exception:

        st.error(default_message)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:2rem;
            font-weight:750;
            margin-bottom:5px;
        ">
            🌍 TerraWatch
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            color:#aeb4bf;
            margin-bottom:28px;
        ">
            City & Disaster Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Navigation")

    page = st.radio(
        "",
        [
            "🏠 Overview",
            "🌦️ Weather",
            "🚨 Disasters",
            "🗺️ Map",
            "📊 Analytics"
        ]
    )

    st.divider()

    health = api_get("/health")

    if health is not None:

        st.success("🟢 API Online")

    else:

        st.error("🔴 API Offline")

        st.caption(
            "Start FastAPI before using TerraWatch."
        )


# ============================================================
# LOAD DATA
# ============================================================

cities = api_get("/cities")

if cities is None:
    cities = []

disasters = api_get("/disasters")

if disasters is None:
    disasters = []


# ============================================================
# OVERVIEW
# ============================================================

if page == "🏠 Overview":

    st.html(
        """
        <div class="hero">

            <div class="hero-small">
                CITY & DISASTER INTELLIGENCE
            </div>

            <div class="hero-title">
                🌍 TerraWatch
            </div>

            <div class="hero-text">
                A unified view of city weather,
                environmental conditions and
                regional disaster activity.
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------------

    total_cities = len(cities)

    total_disasters = len(disasters)

    active_disasters = sum(
        1
        for disaster in disasters
        if str(
            disaster.get("status", "")
        ).lower() == "active"
    )

    temperatures = [
        float(city["temperature"])
        for city in cities
        if city.get("temperature") is not None
    ]

    average_temperature = (
        sum(temperatures) / len(temperatures)
        if temperatures
        else 0
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    🏙️ Cities
                </div>

                <div class="metric-value">
                    {total_cities}
                </div>

            </div>
            """
        )

    with col2:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    🚨 Disasters
                </div>

                <div class="metric-value">
                    {total_disasters}
                </div>

            </div>
            """
        )

    with col3:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    🔴 Active Disasters
                </div>

                <div class="metric-value">
                    {active_disasters}
                </div>

            </div>
            """
        )

    with col4:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    🌡️ Avg Temperature
                </div>

                <div class="metric-value">
                    {average_temperature:.1f}°C
                </div>

            </div>
            """
        )

    st.divider()

    # --------------------------------------------------------
    # RECENT WEATHER
    # --------------------------------------------------------

    st.subheader(
        "🌦️ Recent City Weather"
    )

    if cities:

        weather_df = pd.DataFrame(cities)

        columns = [
            "city_name",
            "state",
            "temperature",
            "humidity",
            "weather_condition"
        ]

        available_columns = [
            column
            for column in columns
            if column in weather_df.columns
        ]

        st.dataframe(
            weather_df[
                available_columns
            ].head(10),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No city data available."
        )

    st.divider()

    # --------------------------------------------------------
    # ACTIVE DISASTERS
    # --------------------------------------------------------

    st.subheader(
        "🚨 Active Disaster Alerts"
    )

    active = [
        disaster
        for disaster in disasters
        if str(
            disaster.get("status", "")
        ).lower() == "active"
    ]

    if active:

        for disaster in active:

            st.html(
                f"""
                <div class="alert-card">

                    <div class="alert-title">
                        🚨
                        {disaster.get(
                            "disaster_type",
                            "Disaster"
                        )}
                    </div>

                    <div class="alert-location">
                        {disaster.get(
                            "region_name",
                            "Unknown"
                        )},
                        {disaster.get(
                            "state",
                            "Unknown"
                        )}
                    </div>

                    <div class="alert-details">

                        Severity:
                        {disaster.get(
                            "severity",
                            "Unknown"
                        )}

                        &nbsp; • &nbsp;

                        Affected:
                        {disaster.get(
                            "affected_population",
                            0
                        ):,}

                    </div>

                </div>
                """
            )

    else:

        st.success(
            "🟢 No active disasters."
        )


# ============================================================
# WEATHER
# ============================================================

elif page == "🌦️ Weather":

    st.title("🌦️ Weather")

    st.write(
        "Search cities and fetch live weather using Open-Meteo."
    )

    # --------------------------------------------------------
    # LIVE WEATHER
    # --------------------------------------------------------

    city_search = st.text_input(
        "City name",
        placeholder="e.g. Hyderabad"
    )

    if st.button(
        "🌤️ Fetch Live Weather"
    ):

        if not city_search.strip():

            st.warning(
                "Please enter a city name."
            )

        else:

            response = api_request(
                "POST",
                "/cities/weather",
                {
                    "city_name":
                        city_search.strip()
                }
            )

            if response is not None:

                if response.status_code in [
                    200,
                    201
                ]:

                    data = response.json()

                    st.success(
                        "✅ Live weather fetched successfully."
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "🌡️ Temperature",
                            f"{data.get('temperature', 0)}°C"
                        )

                    with col2:

                        st.metric(
                            "💧 Humidity",
                            f"{data.get('humidity', 0)}%"
                        )

                    with col3:

                        st.metric(
                            "🌤️ Condition",
                            data.get(
                                "weather_condition",
                                "Unknown"
                            )
                        )

                    st.info(
                        f"{data.get('city_name', '')}, "
                        f"{data.get('state', '')}, "
                        f"{data.get('country', '')}"
                    )

                else:

                    show_api_error(
                        response,
                        "Unable to fetch weather."
                    )

    st.divider()

    # --------------------------------------------------------
    # CITY DATABASE
    # --------------------------------------------------------

    st.subheader(
        "🏙️ City Database"
    )

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        state_filter = st.text_input(
            "Filter by state",
            placeholder="e.g. Telangana"
        )

    with filter_col2:

        min_temperature = st.number_input(
            "Minimum temperature (°C)",
            value=0.0
        )

    params = {}

    if state_filter.strip():

        params["state"] = (
            state_filter.strip()
        )

    if min_temperature > 0:

        params["min_temperature"] = (
            min_temperature
        )

    filtered_cities = api_get(
        "/cities",
        params=params
    )

    if filtered_cities is None:

        filtered_cities = []

    if filtered_cities:

        city_df = pd.DataFrame(
            filtered_cities
        )

        st.dataframe(
            city_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No cities match the selected filters."
        )

    st.divider()

    # ========================================================
    # CITY CRUD
    # ========================================================

    st.subheader(
        "⚙️ Manage Cities"
    )

    city_action = st.radio(
        "Choose an action",
        [
            "➕ Add City",
            "✏️ Edit City",
            "🗑️ Delete City"
        ],
        horizontal=True
    )

    # --------------------------------------------------------
    # ADD CITY
    # --------------------------------------------------------

    if city_action == "➕ Add City":

        st.markdown(
            "### Add a new city"
        )

        with st.form(
            "add_city_form"
        ):

            city_name = st.text_input(
                "City Name",
                placeholder="Hyderabad"
            )

            state = st.text_input(
                "State",
                placeholder="Telangana"
            )

            country = st.text_input(
                "Country",
                value="India"
            )

            temperature = st.number_input(
                "Temperature (°C)",
                value=30.0
            )

            humidity = st.number_input(
                "Humidity (%)",
                min_value=0,
                max_value=100,
                value=50
            )

            weather_condition = st.text_input(
                "Weather Condition",
                placeholder="Sunny"
            )

            submitted = st.form_submit_button(
                "➕ Add City"
            )

        if submitted:

            if not city_name.strip():

                st.error(
                    "City name is required."
                )

            elif not state.strip():

                st.error(
                    "State is required."
                )

            elif not country.strip():

                st.error(
                    "Country is required."
                )

            elif not weather_condition.strip():

                st.error(
                    "Weather condition is required."
                )

            else:

                payload = {
                    "city_name":
                        city_name.strip(),
                    "state":
                        state.strip(),
                    "country":
                        country.strip(),
                    "temperature":
                        temperature,
                    "humidity":
                        humidity,
                    "weather_condition":
                        weather_condition.strip()
                }

                response = api_request(
                    "POST",
                    "/cities",
                    payload
                )

                if response is not None:

                    if response.status_code in [
                        200,
                        201
                    ]:

                        st.success(
                            "✅ City added successfully!"
                        )

                        st.rerun()

                    else:

                        show_api_error(
                            response,
                            "Failed to add city."
                        )

    # --------------------------------------------------------
    # EDIT CITY
    # --------------------------------------------------------

    elif city_action == "✏️ Edit City":

        st.markdown(
            "### Edit an existing city"
        )

        all_cities = (
            api_get("/cities")
            or []
        )

        if not all_cities:

            st.info(
                "No cities available."
            )

        else:

            city_options = {
                f"{city.get('city_name')} "
                f"(ID: {city.get('city_id')})":
                city
                for city in all_cities
            }

            selected_label = st.selectbox(
                "Select city",
                list(
                    city_options.keys()
                )
            )

            selected_city = (
                city_options[
                    selected_label
                ]
            )

            with st.form(
                "edit_city_form"
            ):

                city_name = st.text_input(
                    "City Name",
                    value=selected_city.get(
                        "city_name",
                        ""
                    )
                )

                state = st.text_input(
                    "State",
                    value=selected_city.get(
                        "state",
                        ""
                    )
                )

                country = st.text_input(
                    "Country",
                    value=selected_city.get(
                        "country",
                        ""
                    )
                )

                temperature = st.number_input(
                    "Temperature (°C)",
                    value=float(
                        selected_city.get(
                            "temperature",
                            0
                        )
                    )
                )

                humidity = st.number_input(
                    "Humidity (%)",
                    min_value=0,
                    max_value=100,
                    value=int(
                        selected_city.get(
                            "humidity",
                            0
                        )
                    )
                )

                weather_condition = st.text_input(
                    "Weather Condition",
                    value=selected_city.get(
                        "weather_condition",
                        ""
                    )
                )

                submitted = st.form_submit_button(
                    "💾 Save Changes"
                )

            if submitted:

                payload = {
                    "city_name":
                        city_name.strip(),
                    "state":
                        state.strip(),
                    "country":
                        country.strip(),
                    "temperature":
                        temperature,
                    "humidity":
                        humidity,
                    "weather_condition":
                        weather_condition.strip()
                }

                response = api_request(
                    "PUT",
                    f"/cities/"
                    f"{selected_city['city_id']}",
                    payload
                )

                if response is not None:

                    if response.status_code == 200:

                        st.success(
                            "✅ City updated successfully!"
                        )

                        st.rerun()

                    else:

                        show_api_error(
                            response,
                            "Failed to update city."
                        )

    # --------------------------------------------------------
    # DELETE CITY
    # --------------------------------------------------------

    elif city_action == "🗑️ Delete City":

        st.markdown(
            "### Delete a city"
        )

        all_cities = (
            api_get("/cities")
            or []
        )

        if not all_cities:

            st.info(
                "No cities available."
            )

        else:

            city_options = {
                f"{city.get('city_name')} "
                f"(ID: {city.get('city_id')})":
                city
                for city in all_cities
            }

            selected_label = st.selectbox(
                "Select city to delete",
                list(
                    city_options.keys()
                )
            )

            selected_city = (
                city_options[
                    selected_label
                ]
            )

            st.warning(
                f"You are about to delete "
                f"**{selected_city.get('city_name')}**."
            )

            confirm = st.checkbox(
                "I understand that this cannot be undone."
            )

            if st.button(
                "🗑️ Delete City",
                disabled=not confirm
            ):

                response = api_request(
                    "DELETE",
                    f"/cities/"
                    f"{selected_city['city_id']}"
                )

                if response is not None:

                    if response.status_code in [
                        200,
                        204
                    ]:

                        st.success(
                            "✅ City deleted successfully!"
                        )

                        st.rerun()

                    else:

                        show_api_error(
                            response,
                            "Failed to delete city."
                        )


# ============================================================
# DISASTERS
# ============================================================

elif page == "🚨 Disasters":

    st.title(
        "🚨 Disaster Monitoring"
    )

    st.write(
        "Monitor and manage regional disaster information."
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        disaster_state = st.text_input(
            "State",
            placeholder="Telangana"
        )

    with col2:

        disaster_type_filter = st.selectbox(
            "Disaster Type",
            [
                "All",
                "Flood",
                "Earthquake",
                "Cyclone",
                "Landslide",
                "Drought",
                "Wildfire",
                "Other"
            ]
        )

    with col3:

        severity_filter = st.selectbox(
            "Severity",
            [
                "All",
                "Low",
                "Medium",
                "High",
                "Critical"
            ]
        )

    with col4:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "Active",
                "Monitoring",
                "Resolved"
            ]
        )

    filtered_disasters = disasters.copy()

    if disaster_state.strip():

        filtered_disasters = [
            d
            for d in filtered_disasters
            if disaster_state.lower()
            in str(
                d.get("state", "")
            ).lower()
        ]

    if disaster_type_filter != "All":

        filtered_disasters = [
            d
            for d in filtered_disasters
            if str(
                d.get(
                    "disaster_type",
                    ""
                )
            ).lower()
            ==
            disaster_type_filter.lower()
        ]

    if severity_filter != "All":

        filtered_disasters = [
            d
            for d in filtered_disasters
            if str(
                d.get(
                    "severity",
                    ""
                )
            ).lower()
            ==
            severity_filter.lower()
        ]

    if status_filter != "All":

        filtered_disasters = [
            d
            for d in filtered_disasters
            if str(
                d.get(
                    "status",
                    ""
                )
            ).lower()
            ==
            status_filter.lower()
        ]

    if filtered_disasters:

        disaster_df = pd.DataFrame(
            filtered_disasters
        )

        st.dataframe(
            disaster_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No disasters match the selected filters."
        )

    st.divider()

    # ========================================================
    # DISASTER CRUD
    # ========================================================

    st.subheader(
        "⚙️ Manage Disasters"
    )

    disaster_action = st.radio(
        "Choose an action",
        [
            "➕ Add Disaster",
            "✏️ Edit Disaster",
            "🗑️ Delete Disaster"
        ],
        horizontal=True
    )

    disaster_types = [
        "Flood",
        "Earthquake",
        "Cyclone",
        "Landslide",
        "Drought",
        "Wildfire",
        "Other"
    ]

    severity_values = [
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    status_values = [
        "Active",
        "Monitoring",
        "Resolved"
    ]

    # --------------------------------------------------------
    # ADD DISASTER
    # --------------------------------------------------------

    if disaster_action == "➕ Add Disaster":

        st.markdown(
            "### Add a new disaster"
        )

        with st.form(
            "add_disaster_form"
        ):

            region_name = st.text_input(
                "Region Name",
                placeholder="Hyderabad"
            )

            state = st.text_input(
                "State",
                placeholder="Telangana"
            )

            country = st.text_input(
                "Country",
                value="India"
            )

            disaster_type = st.selectbox(
                "Disaster Type",
                disaster_types
            )

            severity = st.selectbox(
                "Severity",
                severity_values
            )

            affected_population = st.number_input(
                "Affected Population",
                min_value=0,
                value=0,
                step=1
            )

            status = st.selectbox(
                "Status",
                status_values
            )

            description = st.text_area(
                "Description",
                placeholder="Describe the disaster..."
            )

            submitted = st.form_submit_button(
                "➕ Add Disaster"
            )

        if submitted:

            if not region_name.strip():

                st.error(
                    "Region name is required."
                )

            elif not state.strip():

                st.error(
                    "State is required."
                )

            elif not country.strip():

                st.error(
                    "Country is required."
                )

            else:

                payload = {
                    "region_name":
                        region_name.strip(),
                    "state":
                        state.strip(),
                    "country":
                        country.strip(),
                    "disaster_type":
                        disaster_type,
                    "severity":
                        severity,
                    "affected_population":
                        affected_population,
                    "status":
                        status,
                    "description":
                        description.strip()
                }

                response = api_request(
                    "POST",
                    "/disasters",
                    payload
                )

                if response is not None:

                    if response.status_code in [
                        200,
                        201
                    ]:

                        st.success(
                            "✅ Disaster added successfully!"
                        )

                        st.rerun()

                    else:

                        show_api_error(
                            response,
                            "Failed to add disaster."
                        )

    # --------------------------------------------------------
    # EDIT DISASTER
    # --------------------------------------------------------

    elif disaster_action == "✏️ Edit Disaster":

        st.markdown(
            "### Edit an existing disaster"
        )

        all_disasters = (
            api_get("/disasters")
            or []
        )

        if not all_disasters:

            st.info(
                "No disasters available."
            )

        else:

            disaster_options = {
                f"{d.get('disaster_type')} - "
                f"{d.get('region_name')} "
                f"(ID: {d.get('disaster_id')})":
                d
                for d in all_disasters
            }

            selected_label = st.selectbox(
                "Select disaster",
                list(
                    disaster_options.keys()
                )
            )

            selected_disaster = (
                disaster_options[
                    selected_label
                ]
            )

            current_type = selected_disaster.get(
                "disaster_type",
                "Other"
            )

            current_severity = selected_disaster.get(
                "severity",
                "Medium"
            )

            current_status = selected_disaster.get(
                "status",
                "Active"
            )

            with st.form(
                "edit_disaster_form"
            ):

                region_name = st.text_input(
                    "Region Name",
                    value=selected_disaster.get(
                        "region_name",
                        ""
                    )
                )

                state = st.text_input(
                    "State",
                    value=selected_disaster.get(
                        "state",
                        ""
                    )
                )

                country = st.text_input(
                    "Country",
                    value=selected_disaster.get(
                        "country",
                        ""
                    )
                )

                disaster_type = st.selectbox(
                    "Disaster Type",
                    disaster_types,
                    index=(
                        disaster_types.index(
                            current_type
                        )
                        if current_type
                        in disaster_types
                        else len(
                            disaster_types
                        ) - 1
                    )
                )

                severity = st.selectbox(
                    "Severity",
                    severity_values,
                    index=(
                        severity_values.index(
                            current_severity
                        )
                        if current_severity
                        in severity_values
                        else 0
                    )
                )

                affected_population = st.number_input(
                    "Affected Population",
                    min_value=0,
                    value=int(
                        selected_disaster.get(
                            "affected_population",
                            0
                        )
                    ),
                    step=1
                )

                status = st.selectbox(
                    "Status",
                    status_values,
                    index=(
                        status_values.index(
                            current_status
                        )
                        if current_status
                        in status_values
                        else 0
                    )
                )

                description = st.text_area(
                    "Description",
                    value=selected_disaster.get(
                        "description",
                        ""
                    )
                )

                submitted = st.form_submit_button(
                    "💾 Save Changes"
                )

            if submitted:

                payload = {
                    "region_name":
                        region_name.strip(),
                    "state":
                        state.strip(),
                    "country":
                        country.strip(),
                    "disaster_type":
                        disaster_type,
                    "severity":
                        severity,
                    "affected_population":
                        affected_population,
                    "status":
                        status,
                    "description":
                        description.strip()
                }

                response = api_request(
                    "PUT",
                    f"/disasters/"
                    f"{selected_disaster['disaster_id']}",
                    payload
                )

                if response is not None:

                    if response.status_code == 200:

                        st.success(
                            "✅ Disaster updated successfully!"
                        )

                        st.rerun()

                    else:

                        show_api_error(
                            response,
                            "Failed to update disaster."
                        )

    # --------------------------------------------------------
    # DELETE DISASTER
    # --------------------------------------------------------

    elif disaster_action == "🗑️ Delete Disaster":

        st.markdown(
            "### Delete a disaster"
        )

        all_disasters = (
            api_get("/disasters")
            or []
        )

        if not all_disasters:

            st.info(
                "No disasters available."
            )

        else:

            disaster_options = {
                f"{d.get('disaster_type')} - "
                f"{d.get('region_name')} "
                f"(ID: {d.get('disaster_id')})":
                d
                for d in all_disasters
            }

            selected_label = st.selectbox(
                "Select disaster to delete",
                list(
                    disaster_options.keys()
                )
            )

            selected_disaster = (
                disaster_options[
                    selected_label
                ]
            )

            st.warning(
                f"You are about to delete "
                f"**{selected_disaster.get('disaster_type')} "
                f"in {selected_disaster.get('region_name')}**."
            )

            confirm = st.checkbox(
                "I understand that this cannot be undone."
            )

            if st.button(
                "🗑️ Delete Disaster",
                disabled=not confirm
            ):

                response = api_request(
                    "DELETE",
                    f"/disasters/"
                    f"{selected_disaster['disaster_id']}"
                )

                if response is not None:

                    if response.status_code in [
                        200,
                        204
                    ]:

                        st.success(
                            "✅ Disaster deleted successfully!"
                        )

                        st.rerun()

                    else:

                        show_api_error(
                            response,
                            "Failed to delete disaster."
                        )


# ============================================================
# INTERACTIVE MAP
# ============================================================

elif page == "🗺️ Map":

    st.title("🗺️ TerraWatch Map")

    st.caption(
        "Interactive view of monitored cities and disaster activity."
    )

    # --------------------------------------------------------
    # MAP FILTERS
    # --------------------------------------------------------

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        show_cities = st.checkbox(
            "🏙️ Show Cities",
            value=True
        )

    with filter_col2:

        show_disasters = st.checkbox(
            "🚨 Show Disasters",
            value=True
        )

    # --------------------------------------------------------
    # INDIA MAP
    # --------------------------------------------------------

    india_map = folium.Map(
        location=[22.5, 80.0],
        zoom_start=5,
        tiles="CartoDB dark_matter"
    )

    # --------------------------------------------------------
    # CITY MARKERS
    # --------------------------------------------------------

    if show_cities:

        for city in cities:

            latitude = city.get(
                "latitude"
            )

            longitude = city.get(
                "longitude"
            )

            if (
                latitude is None
                or longitude is None
            ):
                continue

            city_name = city.get(
                "city_name",
                "Unknown City"
            )

            state = city.get(
                "state",
                "Unknown State"
            )

            temperature = city.get(
                "temperature",
                "N/A"
            )

            humidity = city.get(
                "humidity",
                "N/A"
            )

            condition = city.get(
                "weather_condition",
                "Unknown"
            )

            popup_html = f"""
                <div style="
                    width:220px;
                    font-family:Arial;
                ">

                    <h4 style="
                        margin-bottom:8px;
                    ">
                        🏙️ {city_name}
                    </h4>

                    <b>State:</b>
                    {state}
                    <br><br>

                    <b>Temperature:</b>
                    {temperature}°C
                    <br>

                    <b>Humidity:</b>
                    {humidity}%
                    <br>

                    <b>Condition:</b>
                    {condition}

                </div>
            """

            folium.Marker(
                location=[
                    latitude,
                    longitude
                ],
                popup=folium.Popup(
                    popup_html,
                    max_width=300
                ),
                tooltip=(
                    f"🏙️ {city_name}"
                ),
                icon=folium.Icon(
                    color="blue",
                    icon="home",
                    prefix="fa"
                )
            ).add_to(india_map)

    # --------------------------------------------------------
    # DISASTER MARKERS
    # --------------------------------------------------------

    if show_disasters:

        for disaster in disasters:

            latitude = disaster.get(
                "latitude"
            )

            longitude = disaster.get(
                "longitude"
            )

            if (
                latitude is None
                or longitude is None
            ):
                continue

            disaster_type = disaster.get(
                "disaster_type",
                "Disaster"
            )

            region = disaster.get(
                "region_name",
                "Unknown"
            )

            state = disaster.get(
                "state",
                "Unknown"
            )

            severity = disaster.get(
                "severity",
                "Unknown"
            )

            status = disaster.get(
                "status",
                "Unknown"
            )

            affected = disaster.get(
                "affected_population",
                0
            )

            # --------------------------------------------
            # MARKER COLOR
            # --------------------------------------------

            if str(
                severity
            ).lower() == "critical":

                marker_color = "darkred"

            elif str(
                severity
            ).lower() == "high":

                marker_color = "red"

            elif str(
                severity
            ).lower() == "medium":

                marker_color = "orange"

            else:

                marker_color = "green"

            popup_html = f"""
                <div style="
                    width:240px;
                    font-family:Arial;
                ">

                    <h4 style="
                        margin-bottom:8px;
                    ">
                        🚨 {disaster_type}
                    </h4>

                    <b>Region:</b>
                    {region}
                    <br>

                    <b>State:</b>
                    {state}
                    <br><br>

                    <b>Severity:</b>
                    {severity}
                    <br>

                    <b>Status:</b>
                    {status}
                    <br>

                    <b>Affected:</b>
                    {affected:,}

                </div>
            """

            folium.Marker(
                location=[
                    latitude,
                    longitude
                ],
                popup=folium.Popup(
                    popup_html,
                    max_width=320
                ),
                tooltip=(
                    f"🚨 {disaster_type} - "
                    f"{region}"
                ),
                icon=folium.Icon(
                    color=marker_color,
                    icon="warning-sign",
                    prefix="glyphicon"
                )
            ).add_to(india_map)

    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 9999;
        background: rgba(20,24,32,0.95);
        padding: 12px 16px;
        border-radius: 10px;
        color: white;
        font-family: Arial;
        font-size: 13px;
        border: 1px solid #444;
    ">

        <b>TerraWatch</b>
        <br><br>

        🔵 City
        <br>

        🟢 Low
        <br>

        🟠 Medium
        <br>

        🔴 High
        <br>

        🔴 Critical

    </div>
    """

    india_map.get_root().html.add_child(
        folium.Element(
            legend_html
        )
    )

    # --------------------------------------------------------
    # DISPLAY MAP
    # --------------------------------------------------------

    st_folium(
        india_map,
        width=None,
        height=650,
        returned_objects=[]
    )

    # --------------------------------------------------------
    # MAP SUMMARY
    # --------------------------------------------------------

    st.divider()

    city_count = len(cities)

    disaster_count = len(disasters)

    active_count = sum(
        1
        for disaster in disasters
        if str(
            disaster.get("status", "")
        ).lower() == "active"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🏙️ Mapped Cities",
            city_count
        )

    with col2:

        st.metric(
            "🚨 Mapped Disasters",
            disaster_count
        )

    with col3:

        st.metric(
            "🔴 Active Disasters",
            active_count
        )

# ============================================================
# ANALYTICS
# ============================================================

elif page == "📊 Analytics":

    import plotly.express as px
    import plotly.graph_objects as go

    st.title("📊 Analytics")

    st.caption(
        "A visual overview of city weather and regional disaster activity."
    )

    # ========================================================
    # DATA
    # ========================================================

    city_df = pd.DataFrame(cities)
    disaster_df = pd.DataFrame(disasters)

    # ========================================================
    # PLOTLY THEME
    # ========================================================

    plotly_layout = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": "#cbd5e1"
        },
        "margin": {
            "l": 20,
            "r": 20,
            "t": 30,
            "b": 20
        }
    }

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    temperatures = pd.Series(dtype=float)

    if (
        not city_df.empty
        and "temperature" in city_df.columns
    ):

        temperatures = pd.to_numeric(
            city_df["temperature"],
            errors="coerce"
        ).dropna()

    total_cities = len(city_df)

    average_temperature = (
        temperatures.mean()
        if not temperatures.empty
        else 0
    )

    total_disasters = len(disaster_df)

    if (
        not disaster_df.empty
        and "affected_population"
        in disaster_df.columns
    ):

        affected_population = pd.to_numeric(
            disaster_df[
                "affected_population"
            ],
            errors="coerce"
        ).fillna(0).sum()

    else:

        affected_population = 0

    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    🏙️ Total Cities
                </div>

                <div class="metric-value">
                    {total_cities}
                </div>

            </div>
            """
        )

    with col2:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    🌡️ Average Temperature
                </div>

                <div class="metric-value">
                    {average_temperature:.1f}°C
                </div>

            </div>
            """
        )

    with col3:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    🚨 Total Disasters
                </div>

                <div class="metric-value">
                    {total_disasters}
                </div>

            </div>
            """
        )

    with col4:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    👥 Affected Population
                </div>

                <div class="metric-value">
                    {int(affected_population):,}
                </div>

            </div>
            """
        )

    st.divider()

    # ========================================================
    # WEATHER INSIGHTS
    # ========================================================

    st.subheader("🌦️ Weather Insights")

    weather_col1, weather_col2 = st.columns(2)

    # --------------------------------------------------------
    # TEMPERATURE DISTRIBUTION
    # --------------------------------------------------------

    with weather_col1:

        st.markdown("#### 🌡️ Temperature Distribution")

        if (
            not city_df.empty
            and "temperature" in city_df.columns
            and "city_name" in city_df.columns
        ):

            temp_df = city_df[
                [
                    "city_name",
                    "temperature"
                ]
            ].copy()

            temp_df["temperature"] = pd.to_numeric(
                temp_df["temperature"],
                errors="coerce"
            )

            temp_df = temp_df.dropna()

            temp_df = temp_df.sort_values(
                "temperature"
            )

            fig = px.bar(
                temp_df,
                x="temperature",
                y="city_name",
                orientation="h",
                text="temperature"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}°C",
                textposition="outside"
            )

            fig.update_layout(
                **plotly_layout,
                xaxis_title="Temperature (°C)",
                yaxis_title="",
                showlegend=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Temperature data unavailable."
            )

    # --------------------------------------------------------
    # CITIES BY STATE
    # --------------------------------------------------------

    with weather_col2:

        st.markdown("#### 🏙️ Cities by State")

        if (
            not city_df.empty
            and "state" in city_df.columns
        ):

            state_counts = (
                city_df["state"]
                .value_counts()
                .reset_index()
            )

            state_counts.columns = [
                "state",
                "count"
            ]

            fig = px.pie(
                state_counts,
                names="state",
                values="count",
                hole=0.58
            )

            fig.update_layout(
                **plotly_layout,
                showlegend=True,
                legend_title=""
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "State data unavailable."
            )

    st.divider()

    # ========================================================
    # DISASTER INSIGHTS
    # ========================================================

    st.subheader("🚨 Disaster Insights")

    disaster_col1, disaster_col2 = st.columns(2)

    # --------------------------------------------------------
    # DISASTER TYPE
    # --------------------------------------------------------

    with disaster_col1:

        st.markdown(
            "#### 🚨 Disaster Type Distribution"
        )

        if (
            not disaster_df.empty
            and "disaster_type"
            in disaster_df.columns
        ):

            type_counts = (
                disaster_df[
                    "disaster_type"
                ]
                .value_counts()
                .reset_index()
            )

            type_counts.columns = [
                "disaster_type",
                "count"
            ]

            fig = px.pie(
                type_counts,
                names="disaster_type",
                values="count",
                hole=0.58
            )

            fig.update_layout(
                **plotly_layout,
                showlegend=True,
                legend_title=""
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Disaster type data unavailable."
            )

    # --------------------------------------------------------
    # SEVERITY
    # --------------------------------------------------------

    with disaster_col2:

        st.markdown(
            "#### ⚠️ Severity Distribution"
        )

        if (
            not disaster_df.empty
            and "severity" in disaster_df.columns
        ):

            severity_counts = (
                disaster_df[
                    "severity"
                ]
                .value_counts()
                .reset_index()
            )

            severity_counts.columns = [
                "severity",
                "count"
            ]

            fig = px.pie(
                severity_counts,
                names="severity",
                values="count",
                hole=0.58
            )

            fig.update_layout(
                **plotly_layout,
                showlegend=True,
                legend_title=""
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Severity data unavailable."
            )

    st.divider()

    # ========================================================
    # ACTIVE VS RESOLVED
    # ========================================================

    status_col1, status_col2 = st.columns(2)

    with status_col1:

        st.markdown(
            "#### 🔴 Active vs Resolved"
        )

        if (
            not disaster_df.empty
            and "status" in disaster_df.columns
        ):

            status_counts = (
                disaster_df[
                    "status"
                ]
                .value_counts()
                .reset_index()
            )

            status_counts.columns = [
                "status",
                "count"
            ]

            fig = px.bar(
                status_counts,
                x="status",
                y="count",
                text="count"
            )

            fig.update_traces(
                textposition="outside"
            )

            fig.update_layout(
                **plotly_layout,
                xaxis_title="",
                yaxis_title="Disasters",
                showlegend=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Disaster status data unavailable."
            )

    # ========================================================
    # AFFECTED POPULATION
    # ========================================================

    with status_col2:

        st.markdown(
            "#### 👥 Affected Population"
        )

        if (
            not disaster_df.empty
            and "affected_population"
            in disaster_df.columns
            and "region_name"
            in disaster_df.columns
        ):

            population_df = disaster_df.copy()

            population_df[
                "affected_population"
            ] = pd.to_numeric(
                population_df[
                    "affected_population"
                ],
                errors="coerce"
            ).fillna(0)

            population_df = (
                population_df
                .groupby(
                    "region_name"
                )[
                    "affected_population"
                ]
                .sum()
                .sort_values(
                    ascending=True
                )
                .tail(8)
                .reset_index()
            )

            fig = px.bar(
                population_df,
                x="affected_population",
                y="region_name",
                orientation="h",
                text="affected_population"
            )

            fig.update_traces(
                texttemplate="%{text:,}",
                textposition="outside"
            )

            fig.update_layout(
                **plotly_layout,
                xaxis_title="People Affected",
                yaxis_title="",
                showlegend=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Affected population data unavailable."
            )

    st.divider()

    # ========================================================
    # TOP AFFECTED REGIONS
    # ========================================================

    st.subheader(
        "📍 Top Affected Regions"
    )

    if (
        not disaster_df.empty
        and "region_name" in disaster_df.columns
        and "affected_population"
        in disaster_df.columns
    ):

        region_df = disaster_df.copy()

        region_df[
            "affected_population"
        ] = pd.to_numeric(
            region_df[
                "affected_population"
            ],
            errors="coerce"
        ).fillna(0)

        top_regions = (
            region_df
            .groupby(
                "region_name"
            )[
                "affected_population"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(5)
            .reset_index()
        )

        # ----------------------------------------------------
        # RANKED REGION CARDS
        # ----------------------------------------------------

        for index, row in top_regions.iterrows():

            rank = index + 1

            region = row[
                "region_name"
            ]

            population = int(
                row[
                    "affected_population"
                ]
            )

            st.html(
                f"""
                <div style="
                    background:#171a22;
                    border:1px solid #292e39;
                    border-radius:14px;
                    padding:14px 18px;
                    margin-bottom:8px;
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">

                    <div>

                        <span style="
                            color:#64748b;
                            font-weight:700;
                            margin-right:15px;
                        ">
                            #{rank}
                        </span>

                        <span style="
                            color:#f8fafc;
                            font-weight:600;
                        ">
                            📍 {region}
                        </span>

                    </div>

                    <div style="
                        color:#cbd5e1;
                        font-weight:600;
                    ">
                        {population:,} people
                    </div>

                </div>
                """
            )

    else:

        st.info(
            "Region data unavailable."
        )