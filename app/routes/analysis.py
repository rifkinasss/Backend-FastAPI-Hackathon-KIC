"""Fuzzy analysis route.

Endpoint:
  GET /api/v1/analysis — Run fuzzy analysis on recent sensor readings
"""

from fastapi import APIRouter, HTTPException, Query

from app.services.analysis_service import get_analysis


router = APIRouter(prefix="/api/v1", tags=["Analysis"])


@router.get("/analysis")
def read_analysis(
    start: str = Query(None, description="Start date (YYYY-MM-DD HH:MM:SS)"),
    end: str = Query(None, description="End date (YYYY-MM-DD HH:MM:SS)"),
):
    """Run fuzzy analysis on sensor readings.

    Without parameters: analyses the last 30 minutes of data.
    With start/end: analyses the specified time range.
    """
    try:
        start_date = start if start and start.strip() else None
        end_date = end if end and end.strip() else None
        return get_analysis(start_date, end_date)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
