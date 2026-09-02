# AgriSim: Synthetic Field Yield Forecasting & Weather Correlation Engine

**AgriSim** is a production-grade backend service and geospatial data processing pipeline that ingests meteorological telemetry, processes spatial field boundaries, and executes agricultural simulation models to forecast crop yields and climate stress metrics.

---

## 🚀 Core Features

1. **Geospatial Field Management:** Register and manage agricultural field boundaries using GeoJSON polygons with PostGIS spatial indexing.
2. **Asynchronous Weather Ingestion:** Scheduled and on-demand background workers (Celery + Redis) that fetch historical and forecasted meteorological data from the NASA POWER API.
3. **Synthetic Yield Simulation:** CPU-bound simulation engine that correlates weather anomalies, soil conditions, and crop growth factors to project harvest metrics.
4. **Resilient Data Pipelines:** Robust error handling, exponential backoff retries for external APIs, and chunked time-series database storage.
5. **RESTful API & Caching:** High-performance endpoints built with FastAPI and Pydantic v2, backed by Redis caching for sub-second retrieval.

---

## 🛠️ Tech Stack

* **Backend Framework:** FastAPI (Python)
* **Package & Environment Manager:** `uv`
* **Database & GIS:** PostgreSQL + PostGIS
* **ORM & Migrations:** SQLAlchemy + Alembic
* **Task Queue & Caching:** Celery + Redis
* **Containerization:** Docker & Docker Compose

---

## 🗄️ Database Schema Architecture

### `fields` Table
* `id` (UUID, Primary Key)
* `name` (String)
* `owner_id` (UUID)
* `boundary` (PostGIS Geometry Polygon, EPSG:4326)
* `total_acres` (Float)
* `created_at` (Timestamp)

### `weather_telemetry` Table
* `id` (BigInt, Primary Key)
* `field_id` (UUID, Foreign Key)
* `date` (Date, Indexed)
* `temperature_max` (Float)
* `temperature_min` (Float)
* `precipitation_mm` (Float)
* `solar_radiation` (Float)

### `simulations` Table
* `id` (UUID, Primary Key)
* `field_id` (UUID, Foreign Key)
* `crop_type` (String)
* `status` (Enum: `pending`, `processing`, `completed`, `failed`)
* `predicted_yield_bushels_per_acre` (Float)
* `confidence_score` (Float)
* `parameters_snapshot` (JSONB)
* `completed_at` (Timestamp)

---

## 🔌 API Endpoints (Planned)

* `POST /api/v1/fields` — Register a new field polygon.
* `GET /api/v1/fields/{id}` — Retrieve field details and acreage.
* `POST /api/v1/simulations` — Trigger a yield simulation run for a specific field and crop type.
* `GET /api/v1/simulations/{id}` — Check simulation status and retrieve results.