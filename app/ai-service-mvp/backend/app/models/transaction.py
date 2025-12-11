"""
Transaction Model - Payment transactions
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CARD = "card"
    SBP = "sbp"        # Russian Fast Payment System
    QR = "qr"
    CASH = "cash"
    WALLET = "wallet"


class Transaction(Base):
    """Payment transaction model"""
    
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relations
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    master_id = Column(UUID(as_uuid=True), ForeignKey("masters.id"), nullable=False)
    
    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="RUB")
    
    # Payment details
    payment_method = Column(String(20), nullable=True)
    gateway_transaction_id = Column(String(255), nullable=True)
    gateway_response = Column(Text, nullable=True)  # Raw gateway response JSON
    
    # Status
    status = Column(String(20), default=TransactionStatus.PENDING.value)
    
    # Payout tracking
    payout_status = Column(String(20), default="pending")  # pending, processed, failed
    payout_at = Column(DateTime, nullable=True)
    payout_reference = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="transactions")
    master = relationship("Master", back_populates="transactions")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "job_id": str(self.job_id),
            "master_id": str(self.master_id),
            "amount": float(self.amount) if self.amount else 0,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "payout_status": self.payout_status,
            "payout_at": self.payout_at.isoformat() if self.payout_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
