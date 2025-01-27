import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import EmailStr, HttpUrl, BaseModel, Field
from enum import Enum
from sqlmodel import Field, Relationship, SQLModel

class InspectionOutcome(str, Enum):
   PASS = "pass"
   FAIL = "fail"
   PENDING = "pending"

# common for both models
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



class Message(SQLModel):
    message: str

  
   
  #for 1nd problem statement
class InspectionStationCreate(BaseModel):
   name: str
   id: uuid.UUID
   description: str
   product_image_url: HttpUrl


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: Optional[str] = None
class Message(SQLModel):
    message: str




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
   #for the 2nd problem
class ImageUploadResponse(BaseModel):
    file_id: uuid.UUID
    file_name: str
    file_url: HttpUrl
    uploaded_at: datetime

   #for the 2nd problem
class TagItem(BaseModel):
    name: str = Field(..., description="Name of the tag")
   #for the 2nd problem
class Tag(BaseModel):
    tags: List[TagItem]

#for 2nd problem statement 
class InspectionTagBase(BaseModel):
   date: datetime
   inspection_type: str
   details: str 
   tags: Tag | None=None
class InspectionTagCreate(InspectionTagBase):
    id: uuid.UUID
   #for the 2nd problem
class InspectionTagUpdate(BaseModel):
   date: Optional[datetime] = None
   inspection_type: Optional[str] = None
   details: Optional[str] = None
   tags: Tag | None=None
   id: uuid.UUID
   #for the 2nd problem
class PaginatedResponse(BaseModel):
   data: List[InspectionTagCreate]
   total: int
   page: int 
   page_size: int


# for 1st problem statement
class PaginatedResponse(BaseModel):
   data: List[InspectionResult]
   total: int
   page: int 
   page_size: int

class Token(BaseModel):
   access_token: str
   token_type: str = "bearer"