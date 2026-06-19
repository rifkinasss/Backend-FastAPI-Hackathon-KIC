from fastapi import APIRouter, Query

from app.services.analysis_service import get_analysis


router = APIRouter()


@router.get("/analysis")
def read_analysis(
    start: str = Query(None, description="Start date (YYYY-MM-DD HH:MM:SS)"),
    end: str = Query(None, description="End date (YYYY-MM-DD HH:MM:SS)"),
):
    try:
        start_date = start if start and start.strip() else None
        end_date = end if end and end.strip() else None
        return get_analysis(start_date, end_date)
    except Exception as exc:
        return {"error": str(exc)}

