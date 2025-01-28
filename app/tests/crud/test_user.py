import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, status,Request,Response
from sqlmodel import Session, create_engine, SQLModel
import tempfile
import shutil
import os
import io
from app.models import (
   InspectionResult, 
   Tag,
   User,
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
from app.crud import InspectionService, ImageUploadService,InspectionTAGCRUD
@pytest.fixture
def test_db():
   engine = create_engine("sqlite:///./test.db")
   SQLModel.metadata.create_all(engine)
   with Session(engine) as session:
       yield session
   SQLModel.metadata.drop_all(engine)
   
@pytest.fixture
def test_upload_dir():
   temp_dir = tempfile.mkdtemp()
   yield temp_dir
   shutil.rmtree(temp_dir)

class TestInspectionService:
   @pytest.fixture
   def service(self, test_db):
       return InspectionService(test_db)

   def test_create_inspection(self, service, test_db):
       user = User(id=uuid4(), email="test@test.com")
       station = InspectionStation(id=uuid4(), owner_id=user.id)
       test_db.add(station)
       test_db.commit()

       inspection = InspectionResultCreate(
           captured_image_url="http://test.com/img.jpg",
           notes="Test inspection"
       )
       
       result = service.create_inspection_result(station.id, inspection, user)
       assert result.station_id == station.id
       assert result.inspection_outcome == InspectionOutcome.PENDING

   def test_get_inspection_results(self, service, test_db):
       user = User(id=uuid4(), email="test@test.com")
       station = InspectionStation(id=uuid4(), owner_id=user.id)
       test_db.add(station)
       test_db.commit()

       for _ in range(5):
           inspection = InspectionResultCreate(captured_image_url="test.jpg")
           service.create_inspection_result(station.id, inspection, user)

       results, total = service.get_inspection_results(user, page_size=3)
       assert total == 5
       assert len(results) == 3

class TestImageUploadService:
   @pytest.fixture
   def service(self, test_upload_dir):
       service = ImageUploadService()
       service.UPLOAD_DIR = test_upload_dir
       return service

   async def test_save_upload_file(self, service):
       test_content = b"test image content"
       test_file = UploadFile(
           filename="test.jpg",
           content_type="image/jpeg",
           file=io.BytesIO(test_content)
       )
       
       result = await service.save_upload_file(test_file)
       assert result.file_name.endswith(".jpg")
       assert os.path.exists(os.path.join(service.UPLOAD_DIR, result.file_name))

class TestInspectionTagCRUD:
   @pytest.fixture
   def crud(self, test_db):
       return InspectionTAGCRUD(test_db)

   def test_create_and_get_inspection(self, crud):
       user_id = uuid4()
       inspection = InspectionTagBase(
           date=datetime.now(),
           inspection_type="test",
           details="test details",
           tags=["tag1", "tag2"]
       )
       
       created = crud.create_inspection(inspection, user_id)
       assert created.inspection_type == "test"
       
       retrieved = crud.get_inspection(created.id, user_id)
       assert retrieved.id == created.id

   def test_update_inspection(self, crud):
       user_id = uuid4()
       inspection = InspectionTagBase(
           date=datetime.now(),
           inspection_type="original",
           details="original"
       )
       created = crud.create_inspection(inspection, user_id)
       
       update = InspectionTagUpdate(inspection_type="updated")
       updated = crud.update_inspection(created.id, user_id, update)
       assert updated.inspection_type == "updated"

   def test_tag_operations(self, crud):
       user_id = uuid4()
       inspection = InspectionTagBase(
           date=datetime.now(),
           inspection_type="test",
           details="test",
           tags=[]
       )
       created = crud.create_inspection(inspection, user_id)
       
       with_tag = crud.add_tag(created.id, user_id, "newtag")
       assert "newtag" in with_tag.tags
       
       without_tag = crud.remove_tag(created.id, user_id, "newtag")
       assert "newtag" not in without_tag.tags