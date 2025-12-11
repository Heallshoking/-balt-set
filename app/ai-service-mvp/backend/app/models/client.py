"""
Client Model - Customers who request services
"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Client(Base):
    """Client (customer) model"""
    
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Personal Information
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    
    # Addresses
    addresses = Column(JSONB, nullable=True)  # [{address, location: {lat, lng}, is_primary}]
    
    # Communication
    preferred_channel = Column(String(20), default="telegram")  # telegram, whatsapp, phone, web
    telegram_chat_id = Column(String(100), nullable=True)
    
    # External IDs
    telegram_user_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="client")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
            "addresses": self.addresses,
            "preferred_channel": self.preferred_channel,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
