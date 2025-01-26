import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import EmailStr, HttpUrl, BaseModel, Field
from enum import Enum

class InspectionOutcome(str, Enum):
   PASS = "pass"
   FAIL = "fail"
   PENDING = "pending"

class UserBase(BaseModel):
   email: EmailStr 
   is_active: bool = True
   is_superuser: bool = False
   full_name: Optional[str] = None

class User(UserBase):
   id: uuid.UUID
   hashed_password: str
   

# for 1st problem statement
class InspectionStation(BaseModel):
   id: uuid.UUID
   name: str
   description: str
   product_image_url: HttpUrl
   criteria: List[str]
   owner_id: uuid.UUID
   created_at: datetime




  
   
  #for 1nd problem statement
class InspectionStationCreate(BaseModel):
   name: str
   id: uuid.UUID
   description: str
   product_image_url: HttpUrl




# for 1st problem statement
class InspectionResult(BaseModel):
   id: uuid.UUID
   station_id: uuid.UUID
   captured_image_url: HttpUrl
   inspection_outcome: InspectionOutcome
   
   notes: Optional[str] = None
   created_at: datetime
   
   # for 1st problem statement
class InspectionResultCreate(BaseModel):
   captured_image_url: HttpUrl
   notes: Optional[str] = None
   
   # for 1st problem statement
class InspectionResultUpdate(BaseModel):
   inspection_outcome: Optional[InspectionOutcome] = None
  
   notes: Optional[str] = None
class ImageUploadResponse(BaseModel):
    file_id: uuid.UUID
    file_name: str
    file_url: HttpUrl
    uploaded_at: datetime


class Tag():
    tags: List[str]
    

#for 2nd problem statement 
class InspectionTagBase(BaseModel):
   date: datetime
   inspection_type: str
   details: str 
   tags: Tag | None=None
class InspectionTagCreate(InspectionTagBase):
   pass

class InspectionTagUpdate(BaseModel):
   date: Optional[datetime] = None
   inspection_type: Optional[str] = None
   details: Optional[str] = None
   tags: Optional[List[str]] = None

# for 1st problem statement
class PaginatedResponse(BaseModel):
   data: List[InspectionResult]
   total: int
   page: int 
   page_size: int

class Token(BaseModel):
   access_token: str
   token_type: str = "bearer"