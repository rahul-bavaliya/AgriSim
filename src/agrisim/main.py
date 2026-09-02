from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from agrisim.api.v1.endpoints import auth, fields, recommendations, weather
from agrisim.schemas.envelope import ResponseEnvelope
from agrisim.core.logging import setup_logging

# --- Initialize Centralized Logging ---
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info(
        "AgriSim API service started successfully with ResponseEnvelope handlers."
    )
    yield
    # Shutdown actions (if any) can go here


app = FastAPI(title="AgriSim API", version="1.0.0", lifespan=lifespan)


# --- Global Exception Handlers for Response Envelope ---
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # Log the error internally here if needed
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Database error occurred. Please ensure migrations are applied.",
            "data": None,
            "error": str(exc.__cause__ or exc),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred.",
            "data": None,
            "error": str(exc),
        },
    )


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Adjust this dictionary to match your exact response envelope structure
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {"code": exc.status_code, "message": exc.detail},
        },
    )


# --- Register Routers ---
app.include_router(fields.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(
    recommendations.router, prefix="/api/v1", tags=["ML Recommendations"]
)
app.include_router(auth.router, prefix="/api/v1")
