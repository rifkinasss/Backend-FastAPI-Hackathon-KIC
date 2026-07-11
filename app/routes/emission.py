"""Emission alert and report routes.

Endpoints:
  GET /api/v1/emission/alert        — Real-time emission alerts
  GET /api/v1/emission/report-daily — Daily emission report
"""

from fastapi import APIRouter, HTTPException, Query

from app.services.emission_service import get_daily_emission_report, get_emission_alert


router = APIRouter(prefix="/api/v1/emission", tags=["Emission"])


@router.get("/alert")
def read_emission_alert(
    window: str = Query("30m", description="Alert window, for example 30m, 1h, or 1d"),
):
    """Check for emission alerts within the specified time window."""
    try:
        return get_emission_alert(window)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/report-daily")
def read_daily_emission_report(
    date: str = Query(None, description="Optional report date in YYYY-MM-DD format"),
):
    """Generate a daily emission report with parameter summaries and recommendations."""
    try:
        return get_daily_emission_report(date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
