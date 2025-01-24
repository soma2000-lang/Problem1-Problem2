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
   

class InspectionStation(BaseModel):
   id: uuid.UUID
   name: str
   description: str
   product_image_url: HttpUrl
   criteria: List[str]
   owner_id: uuid.UUID
   created_at: datetime

class Tag():
    tags: List[str]
    
    



class InspectionTagBase(BaseModel):
   date: datetime
   inspection_type: str
   details: str 
   tags: Tag | None=None
  
   
class InspectionStationCreate(BaseModel):
   name: str
   description: str
   product_image_url: HttpUrl
   criteria: List[str]
   tags: Tag | None=None

class InspectionResult(BaseModel):
   id: uuid.UUID
   station_id: uuid.UUID
   captured_image_url: HttpUrl
   inspection_outcome: InspectionOutcome
   similarity_score: float
   notes: Optional[str] = None
   created_at: datetime
   
class InspectionResultCreate(BaseModel):
   captured_image_url: HttpUrl
   notes: Optional[str] = None
   
class InspectionResultUpdate(BaseModel):
   inspection_outcome: Optional[InspectionOutcome] = None
   similarity_score: Optional[float] = Field(None, ge=0, le=1)
   notes: Optional[str] = None

class PaginatedResponse(BaseModel):
   data: List[InspectionResult]
   total: int
   page: int 
   page_size: int

class Token(BaseModel):
   access_token: str
   token_type: str = "bearer"