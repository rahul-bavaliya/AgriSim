# src/agrisim/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from agrisim.api.v1.endpoints import fields
from agrisim.core.logging import setup_logging
from agrisim.schemas.response_envelope import ResponseEnvelope

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
    envelope = ResponseEnvelope(
        success=False,
        message="Database error occurred. Please ensure migrations are applied.",
        data=None,
        error=str(exc.__cause__ or exc),
    )
    return JSONResponse(status_code=500, content=envelope.model_dump())


@app.exception_handler(HTTPException)
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    envelope = ResponseEnvelope(
        success=False,
        message=exc.detail,
        data=None,
        error={"code": exc.status_code, "message": exc.detail},
    )
    return JSONResponse(status_code=exc.status_code, content=envelope.model_dump())


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    envelope = ResponseEnvelope(
        success=False,
        message="An internal server error occurred.",
        data=None,
        error=str(exc),
    )
    return JSONResponse(status_code=500, content=envelope.model_dump())


# --- Register Routers ---
app.include_router(fields.router, prefix="/api/v1")


@app.get("/", response_model=ResponseEnvelope)
def root():
    return ResponseEnvelope(
        success=True,
        message="AgriSim API is running successfully.",
        data={"service": "AgriSim API", "status": "healthy"},
        error=None,
    )
