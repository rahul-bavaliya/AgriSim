import httpx
from datetime import datetime
from fastapi import HTTPException

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


async def fetch_nasa_seasonal_data(
    lat: float, lon: float, start_date: str, end_date: str
):
    """
    Fetches daily meteorological data from the NASA POWER API
    for a given location, mapping the requested month/day window
    to the historical year 1995.
    """
    # Parse incoming dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # Force the year to 1995 while keeping the requested month and day
    target_year = 1995
    start_dt = start_dt.replace(year=target_year)
    end_dt = end_dt.replace(year=target_year)

    # Format dates from YYYY-MM-DD to YYYYMMDD as required by NASA POWER API
    formatted_start = start_dt.strftime("%Y%m%d")
    formatted_end = end_dt.strftime("%Y%m%d")

    params = {
        "parameters": "T2M,PRECTOTCORR,GWETTOP,ALLSKY_SFC_SW_DWN",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": formatted_start,
        "end": formatted_end,
        "format": "JSON",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(NASA_POWER_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the relevant daily parameter properties
            properties = data.get("properties", {}).get("parameter", {})
            return {
                "status": "success",
                "coordinates": {"lat": lat, "lon": lon},
                "window": {
                    "start": start_date,
                    "end": end_date,
                    "historical_year_applied": target_year,
                },
                "nasa_metrics": properties,
            }
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch data from NASA POWER API: {str(exc)}",
            )
