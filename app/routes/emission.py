from fastapi import APIRouter, HTTPException, Query

from app.services.emission_service import get_daily_emission_report, get_emission_alert


router = APIRouter(prefix="/api/ai/emission")


@router.get("/alert")
def read_emission_alert(
    window: str = Query("30m", description="Alert window, for example 30m, 1h, or 1d"),
):
    try:
        return get_emission_alert(window)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/report-daily")
def read_daily_emission_report(
    date: str = Query(None, description="Optional report date in YYYY-MM-DD format"),
):
    try:
        return get_daily_emission_report(date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

