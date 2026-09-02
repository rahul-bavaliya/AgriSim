def aggregate_nasa_metrics(nasa_metrics: dict) -> dict:
    """
    Aggregates raw daily NASA POWER parameters into seasonal totals, 
    averages, and peaks.
    """
    parameters = nasa_metrics.get("parameter", nasa_metrics) # depends on structure
    
    t2m = parameters.get("T2M", {})
    precip = parameters.get("PRECTOTCORR", {})
    gwettop = parameters.get("GWETTOP", {})
    solar = parameters.get("ALLSKY_SFC_SW_DWN", {})

    # Filter out missing values (NASA usually represents missing data as -999)
    valid_temps = [v for v in t2m.values() if v is not None and v > -900]
    valid_precip = [v for v in precip.values() if v is not None and v > -900]
    valid_soil = [v for v in gwettop.values() if v is not None and v > -900]
    valid_solar = [v for v in solar.values() if v is not None and v > -900]

    return {
        "temperature_summary_c": {
            "average": round(sum(valid_temps) / len(valid_temps), 2) if valid_temps else None,
            "max": max(valid_temps) if valid_temps else None,
            "min": min(valid_temps) if valid_temps else None,
        },
        "precipitation_summary_mm": {
            "total": round(sum(valid_precip), 2) if valid_precip else 0.0,
            "max_daily": max(valid_precip) if valid_precip else None,
        },
        "soil_moisture_summary": {
            "average_top_soil_wetness": round(sum(valid_soil) / len(valid_soil), 4) if valid_soil else None,
        },
        "solar_radiation_summary": {
            "peak_kw_h_m2": max(valid_solar) if valid_solar else None,
            "average": round(sum(valid_solar) / len(valid_solar), 2) if valid_solar else None,
        }
    }