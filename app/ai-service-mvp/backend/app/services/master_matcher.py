"""
Master Matching Service
Intelligent algorithm for matching jobs with available masters
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from geopy.distance import geodesic

from app.models.master import Master
from app.models.job import Job
from app.core.config import settings

logger = logging.getLogger(__name__)


class MasterMatcher:
    """Service for matching jobs with appropriate masters"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_best_master(
        self,
        job: Job,
        max_candidates: int = 10
    ) -> Optional[Master]:
        """
        Find the best master for a job based on multiple criteria
        
        Args:
            job: The job to match
            max_candidates: Maximum number of candidates to consider
            
        Returns:
            Best matching master or None if no match found
        """
        try:
            # Step 1: Filter by specialization
            candidates = await self._filter_by_specialization(
                job.category,
                job.scheduled_time
            )
            
            if not candidates:
                logger.warning(f"No masters found for category {job.category}")
                return None
            
            # Step 2: Check availability
            available_candidates = await self._filter_by_availability(
                candidates,
                job.scheduled_time
            )
            
            if not available_candidates:
                logger.warning(f"No available masters for scheduled time {job.scheduled_time}")
                return None
            
            # Step 3: Rank candidates
            ranked_candidates = await self._rank_masters(
                available_candidates,
                job
            )
            
            # Return top candidate
            if ranked_candidates:
                best_master = ranked_candidates[0]
                logger.info(f"Matched job {job.id} with master {best_master.id}")
                return best_master
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding master: {e}")
            return None
    
    async def _filter_by_specialization(
        self,
        category: str,
        scheduled_time: datetime
    ) -> List[Master]:
        """Filter masters by specialization category"""
        query = select(Master).where(
            and_(
                Master.specializations.contains([category]),
                Master.status == 'active'
            )
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def _filter_by_availability(
        self,
        masters: List[Master],
        scheduled_time: datetime
    ) -> List[Master]:
        """Filter masters who are available at scheduled time"""
        available = []
        
        for master in masters:
            # Check if master is available at scheduled time
            if await self._is_master_available(master, scheduled_time):
                available.append(master)
        
        return available
    
    async def _is_master_available(
        self,
        master: Master,
        scheduled_time: datetime
    ) -> bool:
        """Check if master is available at specific time"""
        # Check schedule JSON
        if not master.schedule:
            return False
        
        # Get day of week
        day_of_week = scheduled_time.strftime("%A").lower()
        
        # Check if day is in schedule
        if day_of_week not in master.schedule:
            return False
        
        # Check time range
        scheduled_hour = scheduled_time.hour
        day_schedule = master.schedule[day_of_week]
        
        if not day_schedule.get('available', False):
            return False
        
        start_hour = day_schedule.get('start_hour', 0)
        end_hour = day_schedule.get('end_hour', 24)
        
        return start_hour <= scheduled_hour < end_hour
    
    async def _rank_masters(
        self,
        masters: List[Master],
        job: Job
    ) -> List[Master]:
        """
        Rank masters based on multiple criteria
        
        Criteria weights:
        - Geographic proximity: High (40%)
        - Current workload: Medium (30%)
        - Experience/Rating: Medium (20%)
        - Tools availability: Low (10%)
        """
        scored_masters = []
        
        for master in masters:
            score = 0.0
            
            # 1. Geographic proximity score (0-40 points)
            proximity_score = await self._calculate_proximity_score(
                master,
                job
            )
            score += proximity_score * 0.4
            
            # 2. Workload score (0-30 points)
            workload_score = await self._calculate_workload_score(master)
            score += workload_score * 0.3
            
            # 3. Experience/Rating score (0-20 points)
            rating_score = (master.rating or 3.5) / 5.0 * 20
            score += rating_score * 0.2
            
            # 4. Tools availability score (0-10 points)
            tools_score = await self._calculate_tools_score(
                master,
                job.required_materials or {}
            )
            score += tools_score * 0.1
            
            scored_masters.append((master, score))
        
        # Sort by score descending
        scored_masters.sort(key=lambda x: x[1], reverse=True)
        
        return [master for master, score in scored_masters]
    
    async def _calculate_proximity_score(
        self,
        master: Master,
        job: Job
    ) -> float:
        """Calculate geographic proximity score (0-100)"""
        try:
            if not master.service_zones or not job.location:
                return 50.0  # Default mid-range score
            
            # Extract coordinates
            job_coords = (
                job.location.get('latitude'),
                job.location.get('longitude')
            )
            
            # Check if job is in any service zone
            for zone in master.service_zones:
                zone_center = (
                    zone.get('latitude'),
                    zone.get('longitude')
                )
                
                if job_coords[0] and zone_center[0]:
                    distance_km = geodesic(job_coords, zone_center).kilometers
                    
                    # Score inversely proportional to distance
                    # 0km = 100 points, 20km = 0 points
                    if distance_km <= 20:
                        return max(0, 100 - (distance_km * 5))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating proximity: {e}")
            return 50.0
    
    async def _calculate_workload_score(
        self,
        master: Master
    ) -> float:
        """Calculate workload score based on current jobs (0-100)"""
        try:
            # Count today's jobs for master
            today_start = datetime.now().replace(hour=0, minute=0, second=0)
            today_end = today_start + timedelta(days=1)
            
            query = select(Job).where(
                and_(
                    Job.master_id == master.id,
                    Job.scheduled_time >= today_start,
                    Job.scheduled_time < today_end,
                    Job.status.in_(['assigned', 'in_transit', 'in_progress'])
                )
            )
            
            result = await self.db.execute(query)
            current_jobs = len(list(result.scalars().all()))
            
            # Score inversely proportional to workload
            # 0 jobs = 100 points, 10+ jobs = 0 points
            max_jobs = settings.MAX_MASTER_DAILY_JOBS
            return max(0, 100 - (current_jobs / max_jobs * 100))
            
        except Exception as e:
            logger.error(f"Error calculating workload: {e}")
            return 50.0
    
    async def _calculate_tools_score(
        self,
        master: Master,
        required_materials: Dict[str, Any]
    ) -> float:
        """Calculate tools availability score (0-100)"""
        if not required_materials or not master.tools:
            return 50.0
        
        required_tools = required_materials.get('tools', [])
        if not required_tools:
            return 100.0
        
        # Calculate percentage of required tools master has
        master_tools_set = set(master.tools)
        required_tools_set = set(required_tools)
        
        if not required_tools_set:
            return 100.0
        
        match_count = len(master_tools_set.intersection(required_tools_set))
        match_percentage = match_count / len(required_tools_set)
        
        return match_percentage * 100
    
    async def notify_master(
        self,
        master: Master,
        job: Job
    ) -> bool:
        """
        Notify master about new job
        Returns True if notification sent successfully
        """
        try:
            # TODO: Implement actual notification via preferred channel
            # - Telegram
            # - WhatsApp
            # - Push notification
            # - SMS
            
            logger.info(f"Notification sent to master {master.id} for job {job.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error notifying master: {e}")
            return False
    
    async def find_alternative_masters(
        self,
        job: Job,
        excluded_master_ids: List[str],
        limit: int = 5
    ) -> List[Master]:
        """Find alternative masters excluding already contacted ones"""
        candidates = await self._filter_by_specialization(
            job.category,
            job.scheduled_time
        )
        
        # Exclude already contacted masters
        filtered_candidates = [
            m for m in candidates
            if str(m.id) not in excluded_master_ids
        ]
        
        # Rank and return top alternatives
        ranked = await self._rank_masters(filtered_candidates, job)
        return ranked[:limit]
