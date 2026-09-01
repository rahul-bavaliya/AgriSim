import logging
from typing import Any
from uuid import UUID
import httpx

from agrisim.core.config import settings
from agrisim.core.constants import (
    DEFAULT_API_LIMIT,
    DEFAULT_BBOX_DELTA,
    DEFAULT_HUMIDITY,
    DEFAULT_PRECIPITATION,
    DEFAULT_STATION_NAME,
    DEFAULT_TEMPERATURE,
    DEFAULT_WIND_SPEED,
    FALLBACK_CONDITION,
    MEASURED_CONDITION_PREFIX,
    TASK_FETCH_WEATHER,
)
from agrisim.core.database import SessionLocal
from agrisim.models.fieldmodel import FieldModel
from agrisim.schemas.weather import WeatherCreate
from agrisim.services.weather import WeatherService
from agrisim.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name=TASK_FETCH_WEATHER)  # type: ignore[misc, reportUnknownMemberType, reportUntypedFunctionDecorator]
def fetch_field_weather(field_id: UUID, lat: float, lon: float) -> dict[str, Any]:
    """
    Fetch live Canadian weather data for a specific field using its coordinates.
    """
    logger.info(
        f"Fetching live Canadian weather for field {field_id} at coordinates ({lat}, {lon})"
    )

    delta = DEFAULT_BBOX_DELTA
    bbox_str = f"{lon - delta},{lat - delta},{lon + delta},{lat + delta}"
    weather_create_data = None

    try:
        params = {
            "f": "json",
            "bbox": bbox_str,
            "limit": DEFAULT_API_LIMIT,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(settings.ECCC_BASE_URL, params=params)
            response.raise_for_status()
            feature_collection = response.json()

            features = feature_collection.get("features", [])
            if features:
                properties = features[0].get("properties", {})
                temp = properties.get("air_temp", DEFAULT_TEMPERATURE)
                humidity = properties.get("rel_hum", DEFAULT_HUMIDITY)
                precip = (
                    properties.get("pcpn_amt_pst1hr", DEFAULT_PRECIPITATION)
                    or DEFAULT_PRECIPITATION
                )
                wind_speed = properties.get(
                    "avg_wnd_spd_10m_pst2mts", DEFAULT_WIND_SPEED
                )
                station_name = properties.get("stn_nam-value", DEFAULT_STATION_NAME)

                weather_create_data = WeatherCreate(
                    field_id=field_id,
                    temperature_celsius=float(temp),
                    humidity_percentage=float(humidity),
                    precipitation_mm=float(precip),
                    wind_speed_kmh=float(wind_speed),
                    condition=f"{MEASURED_CONDITION_PREFIX} ({station_name})",
                )
    except Exception as api_err:
        logger.error(f"Failed to communicate with ECCC API: {str(api_err)}")

    if not weather_create_data:
        weather_create_data = WeatherCreate(
            field_id=field_id,
            temperature_celsius=DEFAULT_TEMPERATURE,
            humidity_percentage=DEFAULT_HUMIDITY,
            precipitation_mm=DEFAULT_PRECIPITATION,
            wind_speed_kmh=DEFAULT_WIND_SPEED,
            condition=FALLBACK_CONDITION,
        )

    db = SessionLocal()
    try:
        weather_record = WeatherService.create_weather_record(
            db=db, weather_in=weather_create_data
        )
        logger.info(
            f"Successfully ingested weather record ID: {weather_record.id} for field: {field_id}"
        )
        return {
            "status": "success",
            "field_id": str(field_id),
            "weather_id": str(weather_record.id),
        }
    except Exception as db_err:
        db.rollback()
        logger.error(
            f"Database error while saving weather for field {field_id}: {str(db_err)}"
        )
        raise
    finally:
        db.close()


@celery_app.task(name="tasks.poll_all_fields_weather")
def poll_all_fields_weather() -> dict[str, Any]:
    """
    Periodic task triggered by Celery Beat to fetch weather for all registered fields.
    """
    logger.info("Celery Beat triggered: Polling weather for all fields...")
    db = SessionLocal()
    dispatched_count = 0
    try:
        fields = db.query(FieldModel).all()
        for field in fields:
            # Extract centroid from field boundary if method exists, else use fallback
            lat, lon = field.get_centroid() if hasattr(field, "get_centroid") else (42.02, -93.63)
            
            fetch_field_weather.delay(field_id=field.id, lat=lat, lon=lon)
            dispatched_count += 1
            
        logger.info(f"Dispatched weather fetch tasks for {dispatched_count} fields.")
        return {"status": "success", "dispatched": dispatched_count}
    except Exception as e:
        logger.error(f"Error in periodic weather polling: {str(e)}")
        raise
    finally:
        db.close()