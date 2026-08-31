from fastapi import FastAPI
from agrisim.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


@app.get("/")
def root():
    return {"message": "Welcome to AgriSim API Engine"}
