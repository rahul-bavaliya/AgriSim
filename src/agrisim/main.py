from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger

from agrisim.api.v1.endpoints import fields
from agrisim.schemas.envelope import ResponseEnvelope
from agrisim.core.logging import setup_logging

# --- Initialize Centralized Logging ---
setup_logging()

app = FastAPI(title="AgriSim API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    logger.info("AgriSim API service started successfully with ResponseEnvelope handlers.")

# --- Global Exception Handlers for Response Envelope ---
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseEnvelope(
            status="error",
            code=exc.status_code,
            message=str(exc.detail),
            data=None
        ).model_dump(),
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseEnvelope(
            status="error",
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            data={"errors": exc.errors()}
        ).model_dump(),
    )

# --- Register Routers ---
app.include_router(fields.router, prefix="/api/v1")