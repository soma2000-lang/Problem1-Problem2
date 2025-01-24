from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import aiofiles
import os
from datetime import datetime
import uuid


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
           similarity_score=0.0,
           notes=inspection.notes,
           created_at=datetime.now()
       )
       
       self.session.add(result)
       self.session.commit()
       self.session.refresh(result)
       return result

   def get_inspection_results(
       self,
       user: User,
       station_id: Optional[UUID] = None,
       page: int = 1,
       page_size: int = 20
   ) -> Tuple[List[InspectionResult], int]:
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
