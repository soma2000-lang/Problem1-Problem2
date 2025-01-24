import pytest
from uuid import uuid4
from datetime import datetime
from sqlmodel import Session, SQLModel, create_engine
from .models import User, InspectionStation, InspectionResult, InspectionResultCreate, InspectionResultUpdate
from .crud import InspectionService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

@pytest.fixture
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def test_user():
    return User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed"
    )

@pytest.fixture
def test_station(session, test_user):
    station = InspectionStation(
        id=uuid4(),
        name="Test Station",
        description="Test Description",
        product="Test Product",
        criteria=["criteria1", "criteria2"],
        owner_id=test_user.id
    )
    session.add(station)
    session.commit()
    return station

@pytest.fixture
def inspection_service(session):
    return InspectionService(session)

def test_create_inspection_result(session, inspection_service, test_user, test_station):
    inspection_data = InspectionResultCreate(
        image_url="http://test.com/image.jpg",
        inspection_outcome="pass",
        notes="Test inspection"
    )
    
    result = inspection_service.create_inspection_result(
        test_station.id,
        inspection_data,
        test_user
    )
    
    assert result.station_id == test_station.id
    assert result.inspection_outcome == "pass"

def test_get_inspection_results(session, inspection_service, test_user, test_station):
    # Create test results
    for i in range(5):
        inspection_service.create_inspection_result(
            test_station.id,
            InspectionResultCreate(
                image_url=f"http://test.com/image{i}.jpg",
                inspection_outcome="pass",
                notes=f"Test inspection {i}"
            ),
            test_user
        )
    
    results, total = inspection_service.get_inspection_results(
        user=test_user,
        page=1,
        page_size=3
    )
    
    assert len(results) == 3
    assert total == 5

def test_update_inspection_result(session, inspection_service, test_user, test_station):
    # Create initial result
    result = inspection_service.create_inspection_result(
        test_station.id,
        InspectionResultCreate(
            image_url="http://test.com/image.jpg",
            inspection_outcome="pass",
            notes="Initial notes"
        ),
        test_user
    )
    
    # Update result
    update_data = InspectionResultUpdate(
        inspection_outcome="fail",
        notes="Updated notes"
    )
    
    updated_result = inspection_service.update_inspection_result(
        result.id,
        update_data,
        test_user
    )
    
    assert updated_result.inspection_outcome == "fail"
    assert updated_result.notes == "Updated notes"

def test_bulk_update_results(session, inspection_service, test_user, test_station):
    # Create test results
    result_ids = []
    for i in range(3):
        result = inspection_service.create_inspection_result(
            test_station.id,
            InspectionResultCreate(
                image_url=f"http://test.com/image{i}.jpg",
                inspection_outcome="pass",
                notes=f"Test inspection {i}"
            ),
            test_user
        )
        result_ids.append(result.id)
    
    # Bulk update
    update_data = InspectionResultUpdate(inspection_outcome="fail")
    updated_results = inspection_service.bulk_update_results(
        result_ids,
        update_data,
        test_user
    )
    
    assert len(updated_results) == 3
    assert all(r.inspection_outcome == "fail" for r in updated_results)

def test_delete_inspection_result(session, inspection_service, test_user, test_station):
    # Create result to delete
    result = inspection_service.create_inspection_result(
        test_station.id,
        InspectionResultCreate(
            image_url="http://test.com/image.jpg",
            inspection_outcome="pass",
            notes="Test notes"
        ),
        test_user
    )
    
    # Delete result
    success = inspection_service.delete_inspection_result(result.id, test_user)
    assert success is True
    
    # Verify deletion
    results, total = inspection_service.get_inspection_results(test_user)
    assert total == 0

def test_search_results(session, inspection_service, test_user, test_station):
    # Create test results
    for product in ["ProductA", "ProductB", "ProductC"]:
        inspection_service.create_inspection_result(
            test_station.id,
            InspectionResultCreate(
                image_url=f"http://test.com/{product}.jpg",
                inspection_outcome="pass",
                notes=f"Test {product}"
            ),
            test_user
        )
    
    results, total = inspection_service.search_results(
        user=test_user,
        search_term="ProductA"
    )
    
    assert total == 1
    assert results[0].notes == "Test ProductA"