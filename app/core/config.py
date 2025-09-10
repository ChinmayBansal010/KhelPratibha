# File: sports_analyzer/app/core/config.py
import os
from typing import Dict, List, Optional

class Settings:
    PROJECT_NAME: str = "AI Sports Talent Assessment"
    API_V1_STR: str = "/api/v1"
    TEMP_DIR: str = "temp_videos"

    SPORTS_CATEGORIES: Dict[str, set] = {
        "track": {"sprint", "hurdles"},
        "jumps": {"high_jump", "long_jump"},
        "throws": {"shot_put", "javelin", "discus"}
    }
    SUPPORTED_SPORTS: List[str] = [
        sport for category in SPORTS_CATEGORIES.values() for sport in category
    ]
    
    _SPORT_TO_CATEGORY_MAP: Dict[str, str] = {
        sport: category
        for category, sports in SPORTS_CATEGORIES.items()
        for sport in sports
    }

    def get_sport_category(self, sport_key: str) -> Optional[str]:
        return self._SPORT_TO_CATEGORY_MAP.get(sport_key)

settings = Settings()

if not os.path.exists(settings.TEMP_DIR):
    os.makedirs(settings.TEMP_DIR)