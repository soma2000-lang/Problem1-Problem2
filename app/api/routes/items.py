from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, status
from sqlmodel import Session,select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from .crud import InspectionService, ImageUploadService,InspectionTAGCRUD
from .database import get_session

from .models import (
   InspectionResult, 
   InspectionResultCreate,
   InspectionResultUpdate,
   ImageUploadResponse,
   PaginatedResponse,
   InspectionOutcome,
   InspectionTagBase,
   InspectionTagUpdate, InspectionTag

)

router = APIRouter()
inspection_service = InspectionService()
image_service = ImageUploadService()


# Create inspection
@router.post("/inspections/", 
   response_model=InspectionResult,
   status_code=status.HTTP_201_CREATED,
   responses={
       201: {"description": "Inspection created successfully"},
       400: {"description": "Invalid input"},
       401: {"description": "Unauthorized"},
       404: {"description": "Station not found"}
   }
)
async def create_inspection(
   name: str,
   description: str,
   file: UploadFile = File(...),
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   try:
       upload_result = await image_service.save_upload_file(file)
       inspection = InspectionResultCreate(
           name=name,
           description=description,
           captured_image_url=upload_result.file_url
       )
       result = inspection_service.create_inspection_result(inspection, current_user)
       return result
   except ValueError as e:
       raise HTTPException(status_code=400, detail=str(e))

# Get single inspection
@router.get("/inspections/{inspection_id}",
   response_model=InspectionResult,
   responses={
       200: {"description": "Success"},
       404: {"description": "Inspection not found"},
       401: {"description": "Unauthorized"}
   }
)
async def get_inspection(
   inspection_id: UUID,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   result = inspection_service.get_inspection_result(inspection_id, current_user)
   if not result:
       raise HTTPException(
           status_code=404,
           detail=f"Inspection with ID {inspection_id} not found"
       )
   return result

# Get filtered/paginated inspections
@router.get("/inspections/",
   response_model=PaginatedResponse,
   responses={
       200: {"description": "Success"},
       401: {"description": "Unauthorized"}
   }
)
async def get_inspections(
   name: Optional[str] = None,
   description: Optional[str] = None,
   page: int = Query(1, gt=0), 
   items_per_page: int = Query(10, gt=0, le=100),
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   results, total = inspection_service.get_inspection_results(
       user=current_user,
       name=name,
       description=description,
       page=page, 
       page_size=items_per_page
   )
   
   return PaginatedResponse(
       data=results,
       total=total,
       page=page,
       page_size=items_per_page
   )

# Update inspection
@router.put("/inspections/{inspection_id}",
   response_model=InspectionResult,
   responses={
       200: {"description": "Inspection updated successfully"},
       400: {"description": "Invalid input"},
       404: {"description": "Inspection not found"},
       401: {"description": "Unauthorized"}
   }
)
async def update_inspection(
   inspection_id: UUID,
   update_data: InspectionResultUpdate,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   try:
       result = inspection_service.update_inspection_result(
           inspection_id, update_data, current_user
       )
       return result
   except ValueError as e:
       raise HTTPException(status_code=404, detail=str(e))

# Delete inspection
@router.delete("/inspections/{inspection_id}",
   status_code=status.HTTP_200_OK,
   responses={
       200: {"description": "Inspection deleted successfully"},
       404: {"description": "Inspection not found"},
       401: {"description": "Unauthorized"}
   }
)
async def delete_inspection(
   inspection_id: UUID,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   if not inspection_service.delete_inspection_result(inspection_id, current_user):
       raise HTTPException(
           status_code=404,
           detail=f"Inspection with ID {inspection_id} not found"
       )
   return {
       "message": f"Inspection with ID {inspection_id} deleted successfully"
   }




    # API Route
@router.post("/inspections/{inspection_id}/tags", response_model=List[TagResponse])
async def add_tags_to_inspection(
    inspection_id: UUID,
    tags: List[TagCreate],
    session: Session = Depends(get_session)
):
    inspection = session.get(InspectionResult, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    created_tags = []
    for tag_data in tags:
        tag = Tag(name=tag_data.name, inspection_id=inspection_id)
        session.add(tag)
        created_tags.append(tag)
    
    session.commit()
    return created_tags

    

@app.post("/upload/image/", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    return await image_service.save_upload_file(file)

@app.post("/inspections/{inspection_id}/image")
async def upload_inspection_image(
    inspection_id: uuid.UUID,
    file: UploadFile = File(...)
):
    uploaded = await image_service.save_upload_file(file)
  
    return uploaded

@router.get("/inspections/", response_model=List[InspectionResult])
async def filter_inspections(
    inspection_type: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    tags: Optional[List[str]] = Query(None),
    outcome: Optional[InspectionOutcome] = Query(None),
    station_id: Optional[UUID] = Query(None),
  
    page: int = Query(1, gt=0),
    page_size: int = Query(20, gt=0, le=100)
):
    query = select(InspectionResult).join(InspectionStation)
    
    if inspection_type:
        query = query.where(InspectionStation.inspection_tag.inspection_type == inspection_type)
    
    if date_from:
        query = query.where(InspectionResult.created_at >= date_from)
    
    if date_to:
        query = query.where(InspectionResult.created_at <= date_to)
        
    if tags:
        query = query.where(InspectionStation.inspection_tag.tags.contains(tags))
        
    if outcome:
        query = query.where(InspectionResult.inspection_outcome == outcome)
        
    if station_id:
        query = query.where(InspectionResult.station_id == station_id)
        
    if similarity_score_min is not None:
        query = query.where(InspectionResult.similarity_score >= similarity_score_min)
        
    if similarity_score_max is not None:
        query = query.where(InspectionResult.similarity_score <= similarity_score_max)
    
    total = session.exec(query).count()
    

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    results = session.exec(query).all()
    return PaginatedResponse(
        data=results,
        total=total,
        page=page,
        page_size=page_size
    )




@router.post("/inspections", response_model=InspectionTag)
def create_inspection(
   inspection: InspectionTagBase,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   crud = InspectionCRUD(session)
   return crud.create_inspection(inspection, current_user.id)

@router.get("/inspections", response_model=List[InspectionTag])
def get_inspections(
   date_from: Optional[datetime] = None,
   date_to: Optional[datetime] = None,
   inspection_type: Optional[str] = None,
   tags: Optional[List[str]] = Query(None),
   page: int = Query(1, gt=0),
   per_page: int = Query(10, gt=0, le=100),
   sort_by: Optional[str] = None,
   sort_desc: bool = False,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   crud = InspectionCRUD(session)
   results, total = crud.get_inspections_with_filters(
       user_id=current_user.id,
       page=page,
       page_size=per_page,
       date_from=date_from,
       date_to=date_to,
       inspection_type=inspection_type,
       tags=tags,
       sort_by=sort_by,
       sort_desc=sort_desc
   )
   return {
       "data": results,
       "total": total,
       "page": page,
       "per_page": per_page
   }

@router.put("/inspections/{inspection_id}", response_model=InspectionTag)
def update_inspection(
   inspection_id: UUID,
   update_data: InspectionTagUpdate,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   crud = InspectionCRUD(session)
   try:
       return crud.update_inspection(inspection_id, current_user.id, update_data)
   except HTTPException as e:
       raise e

@router.delete("/inspections/{inspection_id}")
def delete_inspection(
   inspection_id: UUID,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   crud = InspectionCRUD(session)
   if crud.delete_inspection(inspection_id, current_user.id):
       return {"message": "Visual inspection data deleted successfully."}
   raise HTTPException(status_code=404, detail="Inspection not found")

@router.post("/inspections/{inspection_id}/tags")
def add_tag(
   inspection_id: UUID,
   tag: str,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   crud = InspectionCRUD(session)
   return crud.add_tag(inspection_id, current_user.id, tag)

@router.delete("/inspections/{inspection_id}/tags/{tag}")
def remove_tag(
   inspection_id: UUID,
   tag: str,
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   crud = InspectionCRUD(session)
   return crud.remove_tag(inspection_id, current_user.id, tag)

@router.post("/inspections/bulk/tags")
def bulk_tag_operations(
   inspection_ids: List[UUID],
   tags: List[str],
   operation: str = Query(..., regex="^(add|remove)$"),
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   crud = InspectionCRUD(session)
   return crud.bulk_tag_operations(
       user_id=current_user.id,
       inspection_ids=inspection_ids,
       tags=tags,
       operation=operation
   )

@router.get("/inspections/stats")
def get_inspection_stats(
   days: int = Query(30, gt=0),
   current_user = Depends(get_current_user),
   session: Session = Depends(get_session)
):
   crud = InspectionCRUD(session)
   return crud.get_inspection_stats(current_user.id, days)