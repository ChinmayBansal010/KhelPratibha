# File: sports_analyzer/app/main.py
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings

description = """
**Khel Pratibha: AI-Powered Sports Talent Assessment API** 🇮🇳

This API provides a robust backend for analyzing athletic performance from video clips. 
It uses Google's MediaPipe to extract biomechanical data and provides detailed metrics, talent scores, and actionable feedback.

**Key Features:**
* **Video Upload:** Accepts video files for various athletic events.
* **Biomechanical Analysis:** Extracts dozens of key performance indicators (KPIs).
* **Talent Scoring:** Provides a holistic score based on a weighted model of performance metrics.
* **Actionable Feedback:** Generates coach-like feedback to help athletes improve.

Welcome to the future of sports talent discovery!
"""

tags_metadata = [
    {
        "name": "Analysis",
        "description": "The core endpoints for uploading videos and receiving performance analysis.",
    },
    {
        "name": "Root",
        "description": "A simple health check endpoint to verify the API is running.",
    },
]


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=description,
    version="1.0.0",
    contact={
        "name": "Khel Pratibha Development Team",
        "email": "chinmay8521@gmail.com",
    },
    openapi_tags=tags_metadata,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def read_root():
    
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API!",
        "status": "Healthy",
        "version": app.version
    }

