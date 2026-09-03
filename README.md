# AgriSim 🌾

## Synthetic Field Yield Forecasting & Weather Correlation Engine

**AgriSim** is a production-grade backend service and geospatial data processing pipeline for agricultural field analysis and synthetic crop-yield forecasting.

The platform ingests meteorological telemetry, manages geospatial field boundaries, correlates weather and environmental conditions, and executes agricultural simulation models to forecast crop yields and climate-stress metrics.

---

## 🚀 Features

### 🌍 Geospatial Field Management

* Register agricultural fields using GeoJSON polygon boundaries.
* Store field geometries using **PostGIS**.
* Calculate and persist field acreage.
* Perform spatial queries using PostGIS spatial indexes.
* Retrieve and manage fields through REST APIs.

### 🌦️ Weather Data Ingestion

* Fetch historical and forecast weather data from the **NASA POWER API**.
* Support scheduled and on-demand weather ingestion.
* Process meteorological time-series data asynchronously.
* Store weather telemetry at the field level.
* Implement retry and exponential backoff for external API failures.

### 🌾 Synthetic Yield Simulation

* Execute CPU-intensive agricultural simulations.
* Correlate:

  * Weather anomalies
  * Temperature
  * Precipitation
  * Solar radiation
  * Soil conditions
  * Crop growth factors
* Forecast crop yield in bushels per acre.
* Generate simulation confidence scores.
* Preserve simulation parameters using JSONB snapshots.

### ⚡ Asynchronous Processing

* Use **Celery** for background processing.
* Use **Redis** as the Celery message broker.
* Separate API workloads from long-running simulation and ingestion tasks.
* Support scalable worker processes.

### 🛡️ Resilient Data Pipelines

* Exponential backoff for external API requests.
* Robust exception handling.
* Chunked time-series database writes.
* Simulation failure tracking.
* Persistent simulation status management.

### 🚄 REST API & Caching

* High-performance APIs built with **FastAPI**.
* Request and response validation using **Pydantic v2**.
* Redis-based caching for frequently accessed data.
* Pagination for field listings.
* UUID-based resource identification.

---

# 🏗️ Architecture

AgriSim follows a containerized asynchronous architecture:

```text
                         ┌─────────────────────┐
                         │      API Client     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │      REST API       │
                         └───────┬─────┬───────┘
                                 │     │
                    ┌────────────┘     └─────────────┐
                    ▼                                ▼
           ┌─────────────────┐              ┌─────────────────┐
           │   PostgreSQL    │              │      Redis      │
           │    + PostGIS    │              │ Cache + Broker  │
           └─────────────────┘              └────────┬────────┘
                                                     │
                                             ┌───────┴────────┐
                                             ▼                ▼
                                   ┌─────────────────┐ ┌─────────────────┐
                                   │ Celery Workers  │ │ Celery Workers  │
                                   │ Weather Tasks   │ │ Simulation Tasks│
                                   └────────┬────────┘ └────────┬────────┘
                                            │                   │
                                            ▼                   ▼
                                   ┌─────────────────┐  ┌─────────────────┐
                                   │ NASA POWER API  │  │ Yield Simulation│
                                   └─────────────────┘  │     Engine      │
                                                        └─────────────────┘
```

---

# 🛠️ Technology Stack

| Component             | Technology     |
| --------------------- | -------------- |
| Backend               | FastAPI        |
| Language              | Python 3.12    |
| Package Manager       | uv             |
| Database              | PostgreSQL 16  |
| GIS                   | PostGIS 3.4    |
| ORM                   | SQLAlchemy     |
| Migrations            | Alembic        |
| Spatial ORM           | GeoAlchemy2    |
| Validation            | Pydantic v2    |
| Task Queue            | Celery         |
| Message Broker        | Redis          |
| Cache                 | Redis          |
| HTTP Client           | HTTPX          |
| Geospatial Processing | Shapely        |
| Containerization      | Docker         |
| Orchestration         | Docker Compose |
| Weather Data          | NASA POWER API |

---

# 🗄️ Database Schema

## `fields`

Stores agricultural field boundaries and ownership information.

| Column        | Type                    | Description              |
| ------------- | ----------------------- | ------------------------ |
| `id`          | UUID                    | Primary key              |
| `name`        | String                  | Field name               |
| `owner_id`    | UUID                    | Field owner identifier   |
| `boundary`    | Geometry(Polygon, 4326) | Field boundary           |
| `total_acres` | Float                   | Calculated field acreage |
| `created_at`  | Timestamp               | Creation timestamp       |

### Spatial Configuration

Field boundaries are stored using:

```text
SRID: 4326
Geometry: Polygon
```

PostGIS spatial indexing is used to improve geospatial query performance.

---

## `weather_telemetry`

Stores field-level meteorological observations.

| Column             | Type   | Description                  |
| ------------------ | ------ | ---------------------------- |
| `id`               | BigInt | Primary key                  |
| `field_id`         | UUID   | Foreign key to `fields`      |
| `date`             | Date   | Observation date             |
| `temperature_max`  | Float  | Maximum temperature          |
| `temperature_min`  | Float  | Minimum temperature          |
| `precipitation_mm` | Float  | Precipitation in millimeters |
| `solar_radiation`  | Float  | Solar radiation              |

The `date` column is indexed to optimize time-series queries.

---

## `simulations`

Stores crop-yield simulation requests and results.

| Column                             | Type      | Description             |
| ---------------------------------- | --------- | ----------------------- |
| `id`                               | UUID      | Primary key             |
| `field_id`                         | UUID      | Foreign key to `fields` |
| `crop_type`                        | String    | Crop being simulated    |
| `status`                           | Enum      | Simulation status       |
| `predicted_yield_bushels_per_acre` | Float     | Predicted yield         |
| `confidence_score`                 | Float     | Prediction confidence   |
| `parameters_snapshot`              | JSONB     | Simulation parameters   |
| `completed_at`                     | Timestamp | Completion timestamp    |

### Simulation Status

```text
pending
processing
completed
failed
```

---

# 🔌 API

Base URL:

```text
/api/v1
```

## Fields

### Create Field

```http
POST /api/v1/fields
```

Registers a new agricultural field using a GeoJSON polygon.

---

### List Fields

```http
GET /api/v1/fields/
```

Returns a paginated list of registered fields.

---

### Get Field

```http
GET /api/v1/fields/{id}
```

Retrieves field information, including its boundary and acreage.

---

### Delete Field

```http
DELETE /api/v1/fields/{id}
```

Deletes a field by UUID.

---

## Simulations

### Create Simulation

```http
POST /api/v1/simulations
```

Triggers a yield simulation for a specified field and crop type.

Because simulations may be CPU-intensive, processing is performed asynchronously through Celery.

---

### Get Simulation

```http
GET /api/v1/simulations/{id}
```

Retrieves the current simulation status and, when completed, the forecast results.

---

# 📁 Recommended Project Structure

```text
agrisim/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── agrisim/
│   ├── api/
│   │   └── v1/
│   │       ├── fields.py
│   │       └── simulations.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── field.py
│   │   ├── simulation.py
│   │   └── weather.py
│   │
│   ├── schemas/
│   │   ├── field.py
│   │   ├── simulation.py
│   │   └── weather.py
│   │
│   ├── services/
│   │   ├── field_service.py
│   │   ├── weather_service.py
│   │   └── simulation_service.py
│   │
│   ├── workers/
│   │   ├── celery_app.py
│   │   ├── weather_tasks.py
│   │   └── simulation_tasks.py
│   │
│   └── main.py
│
├── tests/
├── .env
├── .gitignore
├── compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# ⚙️ Local Development

## Prerequisites

Make sure the following tools are installed:

* Python 3.12+
* `uv`
* Docker
* Docker Compose
* PostgreSQL/PostGIS, if running the database outside Docker
* Redis, if running Redis outside Docker

---

## 1. Initialize the Project

Create a new application using `uv`:

```bash
uv init --app
```

---

## 2. Install Dependencies

```bash
uv add "fastapi[standard]" \
    sqlalchemy \
    alembic \
    psycopg2-binary \
    geoalchemy2 \
    celery \
    redis \
    pydantic-settings \
    httpx \
    shapely
```

Then synchronize the environment:

```bash
uv sync
```

> **Note:** If the application uses SQLAlchemy's asynchronous PostgreSQL driver, consider using `asyncpg` and configuring the database URL accordingly.

---

## 3. Activate the Virtual Environment

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

---

# 🔐 Environment Configuration

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql://agrisim:agrisim@localhost:5432/agrisim

REDIS_URL=redis://localhost:6379/0

NASA_POWER_BASE_URL=https://power.larc.nasa.gov/api/temporal

ENVIRONMENT=development

LOG_LEVEL=INFO
```

> Never commit secrets or production credentials to source control.

Add `.env` to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# ▶️ Running the API

Start the FastAPI development server:

```bash
uv run uvicorn agrisim.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

Alternative ReDoc documentation:

```text
http://localhost:8000/redoc
```

---

# 🐳 Docker Compose

AgriSim can run as a multi-container application consisting of:

* FastAPI application
* PostgreSQL + PostGIS
* Redis
* Celery worker

## Start the Application

```bash
docker compose up --build -d
```

---

## Check Container Status

```bash
docker compose ps
```

---

## View API Logs

```bash
docker compose logs -f web
```

---

## View Celery Worker Logs

```bash
docker compose logs -f worker
```

---

## Stop the Environment

```bash
docker compose down
```

To remove containers and associated volumes:

```bash
docker compose down -v
```

> Use `-v` carefully because it removes persistent database volumes.

---

# 🗃️ Database Migrations

AgriSim uses **Alembic** for database schema migrations.

## Create a Migration

After modifying SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "Initial PostGIS tables"
```

Always review an autogenerated migration before applying it to a database.

---

## Apply Migrations

```bash
uv run alembic upgrade head
```

---

## Roll Back One Migration

```bash
uv run alembic downgrade -1
```

---

# 🌦️ Weather Data Pipeline

Weather data is retrieved from the NASA POWER API and processed asynchronously.

A typical ingestion flow is:

```text
NASA POWER API
      │
      ▼
Weather Ingestion Task
      │
      ▼
Validate & Normalize Data
      │
      ▼
Map Weather Data → Field
      │
      ▼
Chunked Database Insert
      │
      ▼
weather_telemetry
```

The pipeline should use retry logic with exponential backoff to handle:

* Network failures
* API timeouts
* Rate limiting
* Temporary NASA POWER API failures
* Invalid upstream responses

---

# 🌾 Yield Simulation Pipeline

Simulation requests are processed asynchronously.

```text
Client
  │
  ▼
POST /simulations
  │
  ▼
Create Simulation
(status = pending)
  │
  ▼
Celery Task
  │
  ▼
Load Field Data
  │
  ├───────────────┐
  ▼               ▼
Weather Data   Field/Soil Data
  │               │
  └───────┬───────┘
          ▼
   Simulation Engine
          │
          ▼
   Yield Calculation
          │
          ▼
Confidence Calculation
          │
          ▼
Update Simulation
(status = completed)
```

If an exception occurs during processing:

```text
status = failed
```

---

# 🧪 Testing

Run the test suite with:

```bash
uv run pytest
```

Run tests with verbose output:

```bash
uv run pytest -v
```

Run a specific test:

```bash
uv run pytest tests/test_fields.py
```

---

# 📊 Performance Considerations

AgriSim is designed for workloads involving geospatial and time-series data.

Key performance considerations include:

### PostgreSQL/PostGIS

* Spatial indexes on field boundaries.
* Index weather telemetry by `field_id` and `date`.
* Use appropriate geometry types and SRIDs.
* Avoid unnecessary geometry transformations during queries.

### Redis

Redis is used for:

* API response caching.
* Celery task brokering.
* Potential task/result coordination.

### Celery

CPU-intensive simulations should not block FastAPI request workers.

Use dedicated Celery workers for:

```text
Weather ingestion
Simulation processing
Other background workloads
```

### Time-Series Data

Weather telemetry should be inserted in batches/chunks rather than individual database transactions whenever possible.

---

# 🔒 Reliability & Error Handling

The application should provide:

* Input validation through Pydantic.
* Database transaction management.
* External API retry policies.
* Exponential backoff.
* Task failure handling.
* Structured application logging.
* Idempotent weather ingestion where possible.
* Simulation status tracking.

Recommended simulation lifecycle:

```text
pending
   │
   ▼
processing
   │
   ├──────────────► failed
   │
   ▼
completed
```

---

# 🩺 Health Checks

The API should expose a health endpoint such as:

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

For production deployments, health checks should verify the availability of critical dependencies such as PostgreSQL and Redis.

---

# 🚀 Production Deployment

For production environments, consider:

* Running FastAPI behind a reverse proxy/load balancer.
* Using multiple FastAPI workers.
* Running dedicated Celery worker containers.
* Separating Celery queues by workload.
* Using managed PostgreSQL/PostGIS where appropriate.
* Using managed Redis where appropriate.
* Enabling database connection pooling.
* Configuring centralized logging.
* Adding application and infrastructure monitoring.
* Securing all environment variables and credentials.
* Running database migrations as part of the deployment process.
* Implementing API authentication and authorization.

---

# 📈 Future Enhancements

Potential future capabilities include:

* Satellite imagery integration.
* NDVI/vegetation-index analysis.
* Soil moisture integration.
* Crop-specific simulation models.
* Historical yield calibration.
* Machine-learning-based yield prediction.
* Field-level climate-risk scoring.
* Drought and heat-stress indicators.
* Growing-degree-day calculations.
* Multi-year weather comparison.
* Spatial weather interpolation.
* Automated simulation scheduling.
* WebSocket-based simulation progress updates.
* Model versioning and experiment tracking.

---

# 🤝 Development Workflow

Recommended workflow:

```bash
# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Start API
uv run uvicorn agrisim.main:app --reload

# Run tests
uv run pytest
```

For Docker-based development:

```bash
docker compose up --build -d

docker compose ps

docker compose logs -f web
```

---

# 📄 License

This project is licensed under the terms specified in the `LICENSE` file.

---

## 🌾 AgriSim

**Synthetic agricultural intelligence through geospatial data, weather telemetry, and simulation-driven yield forecasting.**
