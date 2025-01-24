from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional
from uuid import UUID
from .database import get_session
from .models import (
    InspectionResultCreate,
    InspectionResultUpdate,
    InspectionResultPublic,
    InspectionResultsPublic
)
from .auth import get_current_active_user
from .crud import InspectionService

router = APIRouter()

@router.post("/inspections/", response_model=InspectionResultPublic)
def create_inspection(
    *,
    station_id: UUID,
    inspection: InspectionResultCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    service = InspectionService(session)
    try:
        return service.create_inspection_result(station_id, inspection, current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/inspections/", response_model=InspectionResultsPublic)
def list_inspections(
    station_id: Optional[UUID] = None,
    product: Optional[str] = None,
    outcome: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    service = InspectionService(session)
    results, total = service.get_inspection_results(
        current_user,
        station_id,
        product,
        outcome,
        page,
        page_size
    )
    return InspectionResultsPublic(data=results, count=total)

@router.get("/stations/{station_id}/inspections/", response_model=InspectionResultsPublic)
def get_station_inspections(
    station_id: UUID,
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    service = InspectionService(session)
    try:
        results, total = service.get_station_results(station_id, current_user, page, page_size)
        return InspectionResultsPublic(data=results, count=total)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/inspections/{inspection_id}", response_model=InspectionResultPublic)
def update_inspection(
    inspection_id: UUID,
    update_data: InspectionResultUpdate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    service = InspectionService(session)
    try:
        return service.update_inspection_result(inspection_id, update_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/inspections/{inspection_id}")
def delete_inspection(
    inspection_id: UUID,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    service = InspectionService(session)
    if service.delete_inspection_result(inspection_id, current_user):
        return {"message": "Inspection deleted successfully"}
    raise HTTPException(status_code=404, detail="Inspection not found")

@router.get("/inspections/search/", response_model=InspectionResultsPublic)
def search_inspections(
    q: str,
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    service = InspectionService(session)
    results, total = service.search_results(current_user, q, page, page_size)
    return InspectionResultsPublic(data=results, count=total)

@router.get("/inspections/criteria/", response_model=InspectionResultsPublic)
def filter_by_criteria(
    criteria: list[str],
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    service = InspectionService(session)
    results, total = service.filter_results_by_criteria(current_user, criteria, page, page_size)
    return InspectionResultsPublic(data=results, count=total)