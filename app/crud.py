from app.models import InspectionOutcome,InspectionStation,InspectionStationCreate,InspectionResult,InspectionResultCreate,InspectionResultUpdate,ImageUploadResponse,Tag,InspectionTagBase,InspectionTagCreate, User,PaginatedResponse,InspectionTagUpdate
from fastapi import UploadFile, HTTPException

from uuid import UUID

import aiofiles 
import os

from sqlmodel import Session, select,func
from fastapi import HTTPException
import uuid
from typing import Optional,List,Optional
from datetime import datetime

   # for 1st problem statement
class InspectionService:
   def __init__(self, session: Session):
       self.session = session

   def create_inspection_result(
       self,
       station_id: UUID,
       inspection: InspectionResultCreate,
       user: User
   ) -> InspectionResult:
       station = self.session.get(InspectionStation, station_id)
       if not station or station.owner_id != user.id:
           raise ValueError("Station not found or unauthorized")

       result = InspectionResult(
           station_id=station_id,
           captured_image_url=inspection.captured_image_url,  
           inspection_outcome=InspectionOutcome.PENDING,

           notes=inspection.notes,
           created_at=datetime.now()
       )
       
       self.session.add(result)
       self.session.commit()
       self.session.refresh(result)
       return result

   def get_inspection_results(  # getting results with pagination
       self,
       user: User,
       station_id: Optional[UUID] = None,
       page: int = 1,
       page_size: int = 20
   ) ->  PaginatedResponse:
       query = select(InspectionResult).join(InspectionStation)
       query = query.where(InspectionStation.owner_id == user.id)
       
       if station_id:
           query = query.where(InspectionResult.station_id == station_id)
           
       total = self.session.exec(query).count()
       offset = (page - 1) * page_size
       results = self.session.exec(query.offset(offset).limit(page_size)).all()
       
       return results, total

   def update_inspection_result(
       self,
       result_id: UUID,
       update_data: InspectionResultUpdate,
       user: User
   ) -> InspectionResult:
       query = (
           select(InspectionResult)
           .join(InspectionStation)
           .where(
               InspectionResult.id == result_id,
               InspectionStation.owner_id == user.id
           )
       )
       result = self.session.exec(query).first()
       
       if not result:
           raise ValueError("Inspection result not found or unauthorized")
       
       update_dict = update_data.dict(exclude_unset=True)
       for key, value in update_dict.items():
           setattr(result, key, value)
           
       self.session.add(result)
       self.session.commit()
       self.session.refresh(result)
       return result

   def delete_inspection_result(
       self,
       result_id: UUID,
       user: User
   ) -> bool:
       query = (
           select(InspectionResult)
           .join(InspectionStation) 
           .where(
               InspectionResult.id == result_id,
               InspectionStation.owner_id == user.id
           )
       )
       result = self.session.exec(query).first()
       
       if not result:
           return False
           
       self.session.delete(result)
       self.session.commit()
       return True
# for the image uploading service in the 1st problem
class ImageUploadService:
    def __init__(self):
        self.UPLOAD_DIR = "static/uploads"
        self.ALLOWED_TYPES = {"image/jpeg", "image/png"}
        self.MAX_SIZE = 5 * 1024 * 1024  # 5MB
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    async def save_upload_file(self, upload_file: UploadFile) -> ImageUploadResponse:
        if upload_file.content_type not in self.ALLOWED_TYPES:
            raise HTTPException(400, "Invalid file type")

        file_size = 0
        file_id = uuid.uuid4()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(upload_file.filename)[1]
        new_filename = f"{file_id}_{timestamp}{file_ext}"
        file_path = os.path.join(self.UPLOAD_DIR, new_filename)

        try:
            async with aiofiles.open(file_path, 'wb') as f:
                while chunk := await upload_file.read(8192):
                    file_size += len(chunk)
                    if file_size > self.MAX_SIZE:
                        os.unlink(file_path)
                        raise HTTPException(400, "File too large")
                    await f.write(chunk)

            return ImageUploadResponse(
                file_id=file_id,
                file_name=new_filename,
                file_url=f"/static/uploads/{new_filename}",
                uploaded_at=datetime.now()
            )
        except Exception as e:
            if os.path.exists(file_path):
                os.unlink(file_path)
            raise HTTPException(500, str(e))
class InspectionTAGCRUD:
   def __init__(self, session: Session):
       self.session = session

   def create_inspection(
       self,
       inspection: InspectionTagBase,
       id: UUID
   ) -> InspectionTagCreate:
       db_inspection = InspectionTagCreate(
           **inspection.dict(),
           id=id
       )
       self.session.add(db_inspection)
       self.session.commit()
       self.session.refresh(db_inspection)
       return db_inspection

   def get_inspection(
       self,
       inspection_id:  UUID,
       id: UUID
   ) -> InspectionTagCreate:
       return self.session.exec(
           select(InspectionTagCreate).where(
               InspectionTagCreate.id == inspection_id,

           )
       ).first()

   def get_inspections(
       self,
       user_id: UUID,
       date_from: Optional[datetime] = None,
       date_to: Optional[datetime] = None,
       inspection_type: Optional[str] = None,
       tags: Optional[List[str]] = None,
       skip: int = 0,
       limit: int = 50
   ) -> List[InspectionTagCreate]:
       query = select(InspectionTagCreate).where(InspectionTagCreate.user_id == user_id)

       if date_from:
           query = query.where(InspectionTagCreate.date >= date_from)
       if date_to:
           query = query.where(InspectionTagCreate.date <= date_to)
       if inspection_type:
           query = query.where(InspectionTagCreate.inspection_type == inspection_type)
       if tags:
           query = query.where(InspectionTagCreate.tags.contains(tags))

       return self.session.exec(
           query.offset(skip).limit(limit)
       ).all()

   def update_inspection(
       self,
       inspection_id: UUID,
       user_id: UUID,
       inspection_update: InspectionTagUpdate
   ) -> InspectionTagUpdate:
       inspection = self.get_inspection(inspection_id, user_id)
       if not inspection:
           raise HTTPException(status_code=404, detail="Inspection not found")

       update_data = inspection_update.dict(exclude_unset=True)
       for key, value in update_data.items():
           setattr(inspection, key, value)

       self.session.add(inspection)
       self.session.commit()
       self.session.refresh(inspection)
       return inspection

   def delete_inspection(
       self,
       inspection_id: UUID,
       user_id: UUID
   ) -> bool:
       inspection = self.get_inspection(inspection_id, user_id)
       if not inspection:
           return False

       self.session.delete(inspection)
       self.session.commit()
       return True

   def add_tag(
       self,
       inspection_id: UUID,
       user_id: UUID,
       tag: str
   ) -> InspectionTagCreate:
       inspection = self.get_inspection(inspection_id, user_id)
       if not inspection:
           raise HTTPException(status_code=404, detail="Inspection not found")

       if not inspection.tags:
           inspection.tags = []
       inspection.tags.append(tag)

       self.session.add(inspection)
       self.session.commit()
       self.session.refresh(inspection)
       return inspection

   def remove_tag(
       self,
       inspection_id: UUID,
       user_id: UUID,
       tag: str
   ) -> InspectionTagCreate:
       inspection = self.get_inspection(inspection_id, user_id)
       if not inspection:
           raise HTTPException(status_code=404, detail="Inspection not found")

       if inspection.tags and tag in inspection.tags:
           inspection.tags.remove(tag)

       self.session.add(inspection)
       self.session.commit()
       self.session.refresh(inspection)
       return inspection