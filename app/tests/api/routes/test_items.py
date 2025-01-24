import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from typing import List

from .models import InspectionTagBase, InspectionTag, User, Tag
from .crud import InspectionCRUD

@pytest.fixture
def db_session():
   engine = create_engine("sqlite:///test.db") 
   SQLModel.metadata.create_all(engine)
   with Session(engine) as session:
       yield session
   SQLModel.metadata.drop_all(engine)

@pytest.fixture
def test_user():
   return User(
       id=uuid4(),
       email="test@example.com",
       name="Test User"
   )

@pytest.fixture
def inspection_crud(db_session):
   return InspectionCRUD(db_session)

@pytest.fixture
def sample_inspection():
   return InspectionTagBase(
       date=datetime.now(),
       inspection_type="Quality Check",
       details="Test inspection",
       tags=["test", "quality"]
   )

def test_create_inspection(inspection_crud, test_user, sample_inspection):
   result = inspection_crud.create_inspection(sample_inspection, test_user.id)
   assert isinstance(result, InspectionTag)
   assert result.inspection_type == sample_inspection.inspection_type
   assert result.tags == sample_inspection.tags

def test_get_inspection(inspection_crud, test_user, sample_inspection):
   created = inspection_crud.create_inspection(sample_inspection, test_user.id)
   result = inspection_crud.get_inspection(created.id, test_user.id)
   assert result is not None
   assert result.id == created.id

def test_get_inspections_with_filters(inspection_crud, test_user):
   # Create test data
   dates = [datetime.now() - timedelta(days=i) for i in range(5)]
   inspections = [
       InspectionTagBase(
           date=date,
           inspection_type=f"Type {i}",
           details=f"Details {i}",
           tags=[f"tag{i}", "common"]
       ) for i, date in enumerate(dates)
   ]
   
   created_inspections = [
       inspection_crud.create_inspection(insp, test_user.id)
       for insp in inspections
   ]

   # Test date filter
   results, total = inspection_crud.get_inspections_with_filters(
       user_id=test_user.id,
       date_from=dates[-1],
       date_to=dates[0]
   )
   assert len(results) == 5
   assert total == 5

   # Test tag filter
   results, total = inspection_crud.get_inspections_with_filters(
       user_id=test_user.id,
       tags=["tag0"]
   )
   assert len(results) == 1

def test_update_inspection(inspection_crud, test_user, sample_inspection):
   created = inspection_crud.create_inspection(sample_inspection, test_user.id)
   update_data = {
       "inspection_type": "Updated Type",
       "details": "Updated details"
   }
   updated = inspection_crud.update_inspection(created.id, test_user.id, update_data)
   assert updated.inspection_type == "Updated Type"
   assert updated.details == "Updated details"

def test_delete_inspection(inspection_crud, test_user, sample_inspection):
   created = inspection_crud.create_inspection(sample_inspection, test_user.id)
   result = inspection_crud.delete_inspection(created.id, test_user.id)
   assert result is True
   assert inspection_crud.get_inspection(created.id, test_user.id) is None

def test_tag_operations(inspection_crud, test_user, sample_inspection):
   created = inspection_crud.create_inspection(sample_inspection, test_user.id)
   
   # Test add tag
   updated = inspection_crud.add_tag(created.id, test_user.id, "new_tag")
   assert "new_tag" in updated.tags
   
   # Test remove tag
   updated = inspection_crud.remove_tag(created.id, test_user.id, "new_tag")
   assert "new_tag" not in updated.tags

def test_bulk_tag_operations(inspection_crud, test_user):
   inspections = [
       inspection_crud.create_inspection(
           InspectionTagBase(
               date=datetime.now(),
               inspection_type=f"Type {i}",
               details=f"Details {i}",
               tags=[]
           ),
           test_user.id
       ) for i in range(3)
   ]
   
   inspection_ids = [insp.id for insp in inspections]
   new_tags = ["bulk1", "bulk2"]
   
   # Test bulk add
   updated = inspection_crud.bulk_tag_operations(
       test_user.id, inspection_ids, new_tags, "add"
   )
   assert all(all(tag in insp.tags for tag in new_tags) for insp in updated)
   
   # Test bulk remove
   updated = inspection_crud.bulk_tag_operations(
       test_user.id, inspection_ids, new_tags, "remove"
   )
   assert all(all(tag not in insp.tags for tag in new_tags) for insp in updated)