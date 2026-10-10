from fastapi import APIRouter, Query

from app.stellar import list_flag_events

router = APIRouter()


@router.get("")
def list_events(limit: int = Query(20, ge=1, le=100), cursor: str | None = Query(None, min_length=1, max_length=512)):
    """Read recent `flagged` events from the configured Soroban contract."""
    return list_flag_events(limit=limit, cursor=cursor)
