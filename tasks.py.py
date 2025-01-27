from enum import Enum
from typing import Dict, List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

class TaskPriority(str, Enum):
    TASK1 = "task1"
    TASK2 = "task2" 
    TASK3 = "task3"
    TASK4 = "task4"
    TASK5 = "task5"

class Site(BaseModel):
    id: int
    name: str
    record_capacity: str
    
class Job(BaseModel):
    id: int
    site_id: int
    task: TaskPriority
    status: str

class SitePrioritizer:
    def __init__(self):
        self._capacity_weights = {
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        self._task_weights = {
            TaskPriority.TASK1: 5,
            TaskPriority.TASK2: 4,
            TaskPriority.TASK3: 3,
            TaskPriority.TASK4: 2,
            TaskPriority.TASK5: 1,
        }
    
    def _get_site_capacity_score(self, site: Site) -> int:
        """Calculate score based on site's record capacity."""
        return self._capacity_weights.get(site.record_capacity, 0)
    
    def _get_pending_tasks_score(self, session: Session, site: Site) -> int:
        """Calculate score based on pending tasks and their priorities."""
        # This would be implemented with SQLAlchemy query
        pending_tasks = (
            session.query(Job.task, func.count(Job.id))
            .filter(Job.site_id == site.id, Job.status == "pending")
            .group_by(Job.task)
            .all()
        )
        
        return sum(
            self._task_weights.get(task, 0) * count
            for task, count in pending_tasks
        )
    
    def calculate_priority_score(self, session: Session, site: Site) -> int:
        """Calculate total priority score for a site."""
        try:
            capacity_score = self._get_site_capacity_score(site)
            task_score = self._get_pending_tasks_score(session, site)
            return capacity_score + task_score
        except Exception:
            return 0
    
    def get_prioritized_sites(
        self, 
        session: Session, 
        limit: Optional[int] = None
    ) -> List[Site]:
        """Get sites prioritized by their calculated scores."""
        # Fetch all sites
        sites = session.query(Site).all()
        
        # Calculate scores for each site
        sites_with_scores = [
            (site, self.calculate_priority_score(session, site))
            for site in sites
        ]
        
        # Sort sites by score in descending order
        sorted_sites = sorted(
            sites_with_scores,
            key=lambda x: x[1],
            reverse=True
        )
        
        # Extract sites, optionally limit
        prioritized_sites = [site for site, _ in sorted_sites]
        return prioritized_sites[:limit] if limit else prioritized_sites

# FastAPI App
app = FastAPI()

@app.get("/prioritize-sites/", response_model=List[Site])
def prioritize_sites(
    session: Session = Depends(get_database_session),
    limit: Optional[int] = Query(None, gt=0)
):
    """
    Endpoint to get prioritized sites.
    
    Args:
        limit: Optional maximum number of sites to return
    
    Returns:
        List of sites ordered by priority
    """
    prioritizer = SitePrioritizer()
    return prioritizer.get_prioritized_sites(session, limit=limit)
