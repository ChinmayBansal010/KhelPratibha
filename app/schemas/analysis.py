# File: sports_analyzer/app/schemas/analysis.py
from pydantic import BaseModel
from typing import Dict, Any

class AnalysisResultSchema(BaseModel):
    metrics: Dict[str, Any]
    talent_score: float
    feedback: str

class AnalysisResponse(BaseModel):
    sport: str
    category: str
    analysis_results: AnalysisResultSchema