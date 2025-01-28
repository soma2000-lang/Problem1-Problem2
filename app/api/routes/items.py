from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, status,Request,Response
from sqlmodel import Session,select
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from crud import InspectionService, ImageUploadService,InspectionTAGCRUD
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.api.deps import  CurrentUser, SessionDep
from app.models import (
   InspectionResult, 
   Tag,
   InspectionStation,
   InspectionResultCreate,
   InspectionResultUpdate,
   ImageUploadResponse,
   PaginatedResponse,
   InspectionOutcome,
    InspectionResult,
    InspectionTagCreate,
   InspectionTagBase,
   InspectionTagUpdate

)

router = APIRouter()
inspection_service = InspectionService()
image_service = ImageUploadService()

templates = Jinja2Templates(directory="templates")

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
   current_user =  Depends(CurrentUser),
   session: Session = SessionDep):

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
   current_user =   Depends(CurrentUser),
   session: Session = SessionDep):


   result = inspection_service.get_inspection_result(inspection_id, current_user)
   if not result:
       raise HTTPException(
           status_code=404,
           detail=f"Inspection with ID {inspection_id} not found"
       )
   return result

# Get paginated inspections
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
   current_user =   Depends(CurrentUser),
   session: Session = SessionDep):

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
   current_user =   Depends(CurrentUser),
   session: Session = SessionDep):

   try:
       result = inspection_service.update_inspection_result(
           inspection_id, update_data, current_user
       )
       return result
   except ValueError as e:
       raise HTTPException(status_code=404, detail=str(e))

# Delete inspection 
#Route for 1nd problem
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
   current_user =   Depends(CurrentUser),
   session: Session = SessionDep):

   if not inspection_service.delete_inspection_result(inspection_id, current_user):
       raise HTTPException(
           status_code=404,
           detail=f"Inspection with ID {inspection_id} not found"
       )
   return {
       "message": f"Inspection with ID {inspection_id} deleted successfully"
   }

#Route for 1nd problem
@router.get("/inspections", response_model=List[InspectionResult])
async def list_inspections(
    *,
    session: Session = SessionDep,
    name: Optional[str] = Query(None, description="Filter by inspection name"),
    description: Optional[str] = Query(None, description="Filter by inspection description")
):
    query = select(InspectionStation)
    
   
    if name:
        query = query.where(InspectionStation.name.ilike(f"%{name}%"))
    
    
    if description:
        query = query.where(InspectionStation.description.ilike(f"%{description}%"))

    inspections = session.exec(query).all()
    
    return [InspectionResult.model_validate(inspection) for inspection in inspections]


#Add Tag to Inspection: #Route for 2nd problem
@router.post("/inspections/{inspection_id}/tags", response_model=InspectionTagCreate)
def add_tag_to_inspection(
    tag:UUID,
    tag_data: Tag,
    session: Session = SessionDep
):
    inspection = session.get(Tag, tag)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    

    existing_tags = [tag.name for tag in inspection.tags]
    
   
    if tag_data.tags not in existing_tags:
        new_tag = Tag(name=tag_data.tag)
        session.add(new_tag)
        session.commit()
        session.refresh(inspection)
    
    return InspectionTagCreate(
        id=tag,
        tags=[tag.name for tag in inspection.tags]
    )
    
#Route for 1st problem



@router.post("/upload/image/", response_class=HTMLResponse)
async def upload_image(
    request: Request,
    file: UploadFile = File(...)
):
    try:
       
        upload_result = await image_service.save_upload_file(file)
   
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "success": True,
                "message": "File uploaded successfully!",
                "file_url": upload_result.file_url  # Assuming this is returned by your service
            }
        )
    except Exception as e:
        # Return template with error context
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "success": False,
                "message": str(e)
            }
        )
@router.post("/inspections/{inspection_id}/image")
async def upload_inspection_image(
    inspection_id: UUID,
    file: UploadFile = File(...)
):
    uploaded = await image_service.save_upload_file(file)
  
    return uploaded
# for 2nd model
@router.get("/inspections/", response_model=List[InspectionTagCreate])
async def filter_inspections(
    inspection_type: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    tags: Optional[List[str]] = Query(None),
    outcome: Optional[InspectionOutcome] = Query(None),
 
):
    #query = select(InspectionResult).join(InspectionStation)
    
    if inspection_type:
        query = select(InspectionTagCreate).where(InspectionTagCreate.inspection_type == inspection_type)
    
    if date_from:
        query = select(InspectionTagCreate).where(InspectionTagCreate.created_at >= date_from)
    
    if date_to:
        query = select(InspectionTagCreate).where(InspectionResult.created_at <= date_to)
        
    if tags:
        query = select(InspectionTagCreate).where(InspectionStation.inspection_tag.tags.contains(tags))
        
    if outcome:
        query = select(InspectionTagCreate).where(InspectionResult.inspection_outcome == outcome)
        

   
    inspections = Session.exec(query).all()
    
    return [InspectionTagCreate.model_validate(inspection) for inspection in inspections]


 #Route for 2nd problem
@router.post("/inspections", response_model=InspectionTagCreate)
def create_inspection(
   inspection: InspectionTagBase,
   current_user =   Depends(CurrentUser),
   session: Session = SessionDep
):
   crud = InspectionTAGCRUD(session)
   return crud.create_inspection(inspection, current_user.id)

#Route for 2nd problem
@router.get("/inspections", response_model=List[InspectionTagCreate])
def get_inspections(
   date_from: Optional[datetime] = None,
   date_to: Optional[datetime] = None,
   inspection_type: Optional[str] = None,
   tags: Optional[List[str]] = Query(None),
   page: int = Query(1, gt=0),
   per_page: int = Query(10, gt=0, le=100),
   sort_by: Optional[str] = None,
   sort_desc: bool = False,
   current_user =   Depends(CurrentUser),
   session: Session = SessionDep
):
   crud = InspectionTAGCRUD(session)
   results, total = crud.get_inspections(
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
#Route for 2nd problem
@router.put("/inspections/{inspection_id}", response_model=InspectionTagUpdate)
def update_inspection(
   inspection_id: UUID,
   update_data: InspectionTagUpdate,
   current_user =   Depends(CurrentUser),
   session: Session = SessionDep
):
   crud = InspectionTAGCRUD(session)
   try:
       return crud.update_inspection(inspection_id, current_user.id, update_data)
   except HTTPException as e:
       raise e
 #Route for 2nd problem
@router.delete("/inspections/{inspection_id}")
def delete_inspection(
   inspection_id: UUID,
   current_user =   Depends(CurrentUser),
   session: Session = SessionDep
):
   crud = InspectionTAGCRUD(session)
   if crud.delete_inspection(inspection_id, current_user.id):
       return {"message": "Visual inspection data deleted successfully."}
   raise HTTPException(status_code=404, detail="Inspection not found")



 #Route for 2nd problem
@router.delete("/inspections/{inspection_id}/tags/{tag}")
def remove_tag(
   inspection_id: UUID,
   tag: str,
   current_user =  Depends(CurrentUser),
   session: Session = SessionDep
):
   crud = InspectionTAGCRUD(session)
   return crud.remove_tag(inspection_id, current_user.id, tag)

