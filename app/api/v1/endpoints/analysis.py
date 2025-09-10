# File: sports_analyzer/app/api/v1/endpoints/analysis.py
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.analysis import AnalysisResponse
from app.services import biomechanics, scoring
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=AnalysisResponse)
async def analyze_performance(
    video_file: UploadFile = File(...),
    sport: str = Form(..., enum=settings.SUPPORTED_SPORTS),
    athlete_height_m: float = Form(...)
):
    if not video_file.content_type or not video_file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be a video.")

    sport_category = settings.get_sport_category(sport)
    if not sport_category:
        raise HTTPException(status_code=400, detail="Sport category not found.")

    temp_filename = f"{uuid.uuid4()}"
    video_path = os.path.join(settings.TEMP_DIR, temp_filename)
    
    try:
        with open(video_path, "wb") as buffer:
            buffer.write(await video_file.read())

        landmarks, fps = biomechanics.process_video(video_path)
        if not landmarks:
            raise HTTPException(status_code=400, detail="Could not detect a person in the video.")

        metrics = biomechanics.calculate_all_metrics(sport, landmarks, fps, athlete_height_m)
        if not metrics:
             raise HTTPException(status_code=400, detail=f"Analysis for '{sport}' failed or is not implemented.")
        score = scoring.calculate_talent_score(sport, metrics, athlete_height_m)
        feedback = scoring.generate_feedback(sport, metrics)

        return AnalysisResponse(
            sport=sport,
            category=sport_category,
            analysis_results={
                "metrics": metrics, "talent_score": score, "feedback": feedback
            }
        )
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)