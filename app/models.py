import uuid
from typing import List
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    inspection_stations: list["InspectionStation"] = Relationship(back_populates="owner", cascade_delete=True)

class UserPublic(UserBase):
    id: uuid.UUID

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

class InspectionStationBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(max_length=1000)
    product: str = Field(max_length=255)
    criteria: List[str]

class InspectionStationCreate(InspectionStationBase):
    pass

class InspectionStationUpdate(InspectionStationBase):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    product: str | None = Field(default=None, max_length=255)
    criteria: List[str] | None = None

class InspectionStation(InspectionStationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    owner: User = Relationship(back_populates="inspection_stations")
    inspection_results: list["InspectionResult"] = Relationship(back_populates="station")

class InspectionStationPublic(InspectionStationBase):
    id: uuid.UUID
    owner_id: uuid.UUID

class InspectionStationsPublic(SQLModel):
    data: list[InspectionStationPublic]
    count: int

class InspectionResultBase(SQLModel):
    image_url: str = Field(max_length=2083)  # Max URL length
    inspection_outcome: str = Field(max_length=50)
    notes: str | None = Field(default=None, max_length=1000)

class InspectionResultCreate(InspectionResultBase):
    pass

class InspectionResult(InspectionResultBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    station_id: uuid.UUID = Field(foreign_key="inspectionstation.id", nullable=False)
    station: InspectionStation = Relationship(back_populates="inspection_results")

class InspectionResultPublic(InspectionResultBase):
    id: uuid.UUID
    station_id: uuid.UUID

class InspectionResultsPublic(SQLModel):
    data: list[InspectionResultPublic]
    count: int

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str | None = None

class Message(SQLModel):
    message: str