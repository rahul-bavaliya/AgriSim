from datetime import datetime
from typing import List, Dict


def get_upcoming_seasons() -> List[Dict[str, str]]:
    """
    Evaluates the current date and returns structured options
    for upcoming agricultural seasons and their active months.
    """
    current_year = datetime.now().year
    current_month = datetime.now().month

    seasons = []

    # Logic based on calendar progression
    if current_month <= 9:
        # If we are early-to-mid year, Fall/Winter is coming up next
        seasons.append(
            {
                "season_name": "Fall / Winter Cover Crop",
                "code": f"FALL_{current_year}",
                "start_date": f"{current_year}-09-15",
                "end_date": f"{current_year}-11-30",
                "description": "Ideal for soil stabilization, moisture retention, and nitrogen fixing during off-season.",
            }
        )

    # Always offer the upcoming primary Spring/Summer season
    next_spring_year = current_year if current_month < 4 else current_year + 1
    seasons.append(
        {
            "season_name": "Spring / Summer Main Season",
            "code": f"SPRING_{next_spring_year}",
            "start_date": f"{next_spring_year}-05-01",
            "end_date": f"{next_spring_year}-09-30",
            "description": "Primary commercial crop production window (optimal thermal and precipitation profile).",
        }
    )

    return seasons
