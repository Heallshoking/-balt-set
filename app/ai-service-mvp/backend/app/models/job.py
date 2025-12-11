"""
Job Model - Work orders connecting clients with masters
"""

from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class JobStatus(str, enum.Enum):
    CREATED = "created"           # Job created, waiting for assignment
    ASSIGNED = "assigned"         # Master assigned, waiting for acceptance
    ACCEPTED = "accepted"         # Master accepted the job
    IN_TRANSIT = "in_transit"     # Master is on the way
    IN_PROGRESS = "in_progress"   # Work in progress
    COMPLETED = "completed"       # Work completed, waiting for payment
    PAID = "paid"                 # Payment received
    CANCELLED = "cancelled"       # Job cancelled


class Job(Base):
    """Job (work order) model"""
    
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relations
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    master_id = Column(UUID(as_uuid=True), ForeignKey("masters.id"), nullable=True)
    
    # Job Details
    category = Column(String(50), nullable=False)  # electrical, plumbing, appliances, renovation
    client_description = Column(Text, nullable=False)
    ai_diagnosis = Column(Text, nullable=True)
    
    # Media
    media_files = Column(ARRAY(Text), nullable=True)  # URLs of photos/videos
    
    # Location
    address = Column(Text, nullable=False)
    location = Column(JSONB, nullable=True)  # {latitude, longitude}
    
    # Timing
    scheduled_time = Column(DateTime, nullable=True)
    urgency = Column(String(20), default="normal")  # critical, urgent, normal, flexible
    estimated_duration_hours = Column(Float, default=1.0)
    
    # Pricing
    client_cost = Column(Numeric(10, 2), nullable=False)
    master_earnings = Column(Numeric(10, 2), nullable=False)
    platform_commission = Column(Numeric(10, 2), nullable=False)
    
    # Instructions for master
    instructions = Column(JSONB, nullable=True)
    required_materials = Column(JSONB, nullable=True)
    required_tools = Column(ARRAY(Text), nullable=True)
    
    # Communication history
    dialogue_history = Column(JSONB, nullable=True)
    
    # Status tracking
    status = Column(String(20), default=JobStatus.CREATED.value)
    status_history = Column(JSONB, nullable=True)  # [{status, timestamp, note}]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Source channel
    source_channel = Column(String(20), default="web")  # telegram, web, phone, whatsapp
    
    # Relationships
    client = relationship("Client", back_populates="jobs")
    master = relationship("Master", back_populates="jobs")
    transactions = relationship("Transaction", back_populates="job")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "client_id": str(self.client_id) if self.client_id else None,
            "master_id": str(self.master_id) if self.master_id else None,
            "category": self.category,
            "client_description": self.client_description,
            "ai_diagnosis": self.ai_diagnosis,
            "media_files": self.media_files,
            "address": self.address,
            "location": self.location,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "urgency": self.urgency,
            "estimated_duration_hours": self.estimated_duration_hours,
            "client_cost": float(self.client_cost) if self.client_cost else 0,
            "master_earnings": float(self.master_earnings) if self.master_earnings else 0,
            "platform_commission": float(self.platform_commission) if self.platform_commission else 0,
            "instructions": self.instructions,
            "required_materials": self.required_materials,
            "required_tools": self.required_tools,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "source_channel": self.source_channel
        }
    
    def update_status(self, new_status: str, note: str = None):
        """Update job status with history tracking"""
        if self.status_history is None:
            self.status_history = []
        
        self.status_history.append({
            "from_status": self.status,
            "to_status": new_status,
            "timestamp": datetime.utcnow().isoformat(),
            "note": note
        })
        
        self.status = new_status
        
        # Update timing fields
        if new_status == JobStatus.ASSIGNED.value:
            self.assigned_at = datetime.utcnow()
        elif new_status == JobStatus.IN_PROGRESS.value:
            self.started_at = datetime.utcnow()
        elif new_status in [JobStatus.COMPLETED.value, JobStatus.PAID.value]:
            self.completed_at = datetime.utcnow()
