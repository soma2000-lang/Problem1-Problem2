from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import select, Session
from .models import (
    InspectionStation,
    InspectionStationCreate,
    InspectionStationUpdate,
    InspectionResult,
    InspectionResultCreate,
    User
)

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

        result = InspectionResult.from_orm(inspection)
        result.station_id = station_id
        
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result

    def get_inspection_results(
        self,
        user: User,
        station_id: Optional[UUID] = None,
        product: Optional[str] = None,
        outcome: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InspectionResult], int]:
        query = select(InspectionResult).join(InspectionStation)
        

        query = query.where(InspectionStation.owner_id == user.id)
        
       
        if station_id:
            query = query.where(InspectionResult.station_id == station_id)
        if product:
            query = query.where(InspectionStation.product == product)
        if outcome:
            query = query.where(InspectionResult.inspection_outcome == outcome)
        
        # Get total count
        total = self.session.exec(query).count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        results = self.session.exec(
            query.offset(offset).limit(page_size)
        ).all()
        
        return results, total

    def get_station_results(
        self,
        station_id: UUID,
        user: User,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InspectionResult], int]:
        
        station = self.session.get(InspectionStation, station_id)
        if not station or station.owner_id != user.id:
            raise ValueError("Station not found or unauthorized")
        
        query = select(InspectionResult).where(
            InspectionResult.station_id == station_id
        )
        
        total = self.session.exec(query).count()
        offset = (page - 1) * page_size
        
        results = self.session.exec(
            query.offset(offset).limit(page_size)
        ).all()
        
        return results, total
    def update_inspection_result(
        self,
        result_id: UUID,
        update_data: InspectionResultUpdate,
        user: User
    ) -> InspectionResult:
        result = (
            self.session.exec(
                select(InspectionResult)
                .join(InspectionStation)
                .where(
                    InspectionResult.id == result_id,
                    InspectionStation.owner_id == user.id
                )
            )
            .first()
        )
        
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
        result = (
            self.session.exec(
                select(InspectionResult)
                .join(InspectionStation)
                .where(
                    InspectionResult.id == result_id,
                    InspectionStation.owner_id == user.id
                )
            )
            .first()
        )
        
        if not result:
            return False
            
        self.session.delete(result)
        self.session.commit()
        return True


    def filter_results_by_criteria(
        self,
        user: User,
        criteria: List[str],
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InspectionResult], int]:
        query = (
            select(InspectionResult)
            .join(InspectionStation)
            .where(InspectionStation.owner_id == user.id)
            .where(InspectionStation.criteria.contains(criteria))
        )
        
        total = self.session.exec(query).count()
        offset = (page - 1) * page_size
        
        results = self.session.exec(
            query.offset(offset).limit(page_size)
        ).all()
        
        return results, total

    def search_results(
        self,
        user: User,
        search_term: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InspectionResult], int]:
        query = (
            select(InspectionResult)
            .join(InspectionStation)
            .where(InspectionStation.owner_id == user.id)
            .where(
                (InspectionStation.name.contains(search_term)) |
                (InspectionStation.description.contains(search_term)) |
                (InspectionStation.product.contains(search_term))
            )
        )
        
        total = self.session.exec(query).count()
        offset = (page - 1) * page_size
        
        results = self.session.exec(
            query.offset(offset).limit(page_size)
        ).all()
        
        return results, total
    def search_results(
        self,
        user: User,
        search_term: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InspectionResult], int]:
        query = (
            select(InspectionResult)
            .join(InspectionStation)
            .where(InspectionStation.owner_id == user.id)
            .where(
                (InspectionStation.name.contains(search_term)) |
                (InspectionStation.description.contains(search_term)) |
                (InspectionStation.product.contains(search_term))
            )
        )
        
        total = self.session.exec(query).count()
        offset = (page - 1) * page_size
        results = self.session.exec(query.offset(offset).limit(page_size)).all()
        
        return results, total