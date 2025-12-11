"""
Master Model - Service professionals who perform work
"""

from sqlalchemy import Column, String, Text, Float, DateTime, Enum, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class MasterStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING = "pending"


class Master(Base):
    """Master (service professional) model"""
    
    __tablename__ = "masters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Personal Information
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), nullable=True)
    
    # Professional Info
    specializations = Column(ARRAY(Text), nullable=False, default=list)
    experience_years = Column(Float, default=0.0)
    
    # Service Area
    service_zones = Column(JSONB, nullable=True)  # [{name, latitude, longitude, radius_km}]
    max_distance_km = Column(Float, default=20.0)
    
    # Schedule & Availability
    schedule = Column(JSONB, nullable=True)  # {monday: {available: true, start_hour: 8, end_hour: 18}}
    current_location = Column(JSONB, nullable=True)  # {latitude, longitude, updated_at}
    
    # Tools & Equipment
    tools = Column(ARRAY(Text), nullable=True)
    has_own_transport = Column(String(50), default="no")  # no, car, public
    
    # Financial
    bank_details = Column(Text, nullable=True)  # Encrypted
    tax_id = Column(String(50), nullable=True)  # INN
    
    # Terminal
    terminal_type = Column(String(20), default="mobile")  # mobile, physical
    terminal_activated = Column(DateTime, nullable=True)
    
    # Communication preferences
    preferred_channel = Column(String(20), default="telegram")  # telegram, whatsapp, phone
    telegram_chat_id = Column(String(100), nullable=True)
    
    # Rating & Stats
    rating = Column(Float, default=0.0)
    total_jobs = Column(Float, default=0)
    completed_jobs = Column(Float, default=0)
    
    # Status
    status = Column(Enum(MasterStatus), default=MasterStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="master")
    transactions = relationship("Transaction", back_populates="master")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
            "specializations": self.specializations or [],
            "experience_years": self.experience_years,
            "service_zones": self.service_zones,
            "max_distance_km": self.max_distance_km,
            "schedule": self.schedule,
            "tools": self.tools or [],
            "has_own_transport": self.has_own_transport,
            "terminal_type": self.terminal_type,
            "terminal_activated": self.terminal_activated.isoformat() if self.terminal_activated else None,
            "preferred_channel": self.preferred_channel,
            "rating": self.rating,
            "total_jobs": int(self.total_jobs),
            "completed_jobs": int(self.completed_jobs),
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def is_available_at(self, target_datetime: datetime) -> bool:
        """Check if master is available at given datetime"""
        if not self.schedule:
            return False
        
        day_name = target_datetime.strftime("%A").lower()
        
        if day_name not in self.schedule:
            return False
        
        day_schedule = self.schedule[day_name]
        
        if not day_schedule.get("available", False):
            return False
        
        hour = target_datetime.hour
        start_hour = day_schedule.get("start_hour", 0)
        end_hour = day_schedule.get("end_hour", 24)
        
        return start_hour <= hour < end_hour
    
    def has_specialization(self, category: str) -> bool:
        """Check if master has required specialization"""
        if not self.specializations:
            return False
        return category in self.specializations
