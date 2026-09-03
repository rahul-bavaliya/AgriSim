# --- Celery Tasks ---
TASK_FETCH_WEATHER = "fetch_field_weather"

# --- Weather API & Ingestion Defaults ---
DEFAULT_STATION_NAME = "ECCC Auto Station"
FALLBACK_CONDITION = "Estimated / API Fallback"
MEASURED_CONDITION_PREFIX = "Measured"

DEFAULT_BBOX_DELTA = 0.5
DEFAULT_API_LIMIT = 1

# Default Fallback Weather Values
DEFAULT_TEMPERATURE = 21.0
DEFAULT_HUMIDITY = 55.0
DEFAULT_PRECIPITATION = 0.0
DEFAULT_WIND_SPEED = 12.0

# --- Field & Geometry Constants ---
DEFAULT_SRID = 4326
DEFAULT_GEOMETRY_TYPE = "POLYGON"

# --- Test Suite Strings & Mock Data ---
TEST_FIELD_NAME = "Test Research Plot A"
TEST_CROP_TYPE = "Soybeans"
TEST_MOCK_STATION_NAME = "Ottawa/Gatineau"
TEST_MOCK_AIR_TEMP = 20.4
TEST_MOCK_HUMIDITY = 100.0
TEST_MOCK_PRECIP = 0.2
TEST_MOCK_WIND_SPEED = 10.4
