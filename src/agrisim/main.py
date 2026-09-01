from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from agrisim.api.v1.endpoints import fields
from agrisim.schemas.envelope import ResponseEnvelope

app = FastAPI(title="AgriSim API", version="1.0.0")

# --- Global Exception Handlers for Response Envelope ---

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
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