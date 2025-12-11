"""
Master Terminal API - Job management and payment processing for masters.

Handles:
- View assigned jobs
- Accept/reject jobs
- Update job status (in transit, in progress, completed)
- Process payments
- View earnings
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

router = APIRouter()


# ============= In-Memory Storage (MVP) =============
# In production: use database

# Import masters_db from master.py
from .master import masters_db

jobs_db: Dict[str, Dict[str, Any]] = {}
transactions_db: Dict[str, Dict[str, Any]] = {}


# ============= Request/Response Models =============

class JobStatusUpdate(BaseModel):
    """Job status update request"""
    status: str = Field(..., description="New status: accepted, in_transit, in_progress, completed")
    note: Optional[str] = None
    location: Optional[Dict[str, float]] = None  # {latitude, longitude}


class PaymentProcessRequest(BaseModel):
    """Payment processing request"""
    job_id: str
    payment_method: str = "card"  # card, cash, sbp
    amount: Optional[float] = None  # If not provided, uses job.client_cost


class CreateJobRequest(BaseModel):
    """Create a new job (from AI orchestrator)"""
    category: str
    client_description: str
    address: str
    client_cost: float
    master_earnings: float
    platform_commission: float
    urgency: str = "normal"
    client_phone: Optional[str] = None
    client_name: Optional[str] = None
    instructions: Optional[Dict[str, Any]] = None
    required_materials: Optional[List[Dict[str, Any]]] = None
    media_files: Optional[List[str]] = None


# ============= API Endpoints =============

@router.get("/jobs/{master_id}")
async def get_master_jobs(
    master_id: str,
    status: Optional[str] = None,
    limit: int = 20
):
    """Get jobs assigned to a master"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    master_jobs = [
        job for job in jobs_db.values()
        if job.get("master_id") == master_id
    ]
    
    if status:
        master_jobs = [j for j in master_jobs if j.get("status") == status]
    
    # Sort by created_at descending
    master_jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {
        "master_id": master_id,
        "total": len(master_jobs),
        "jobs": master_jobs[:limit]
    }


@router.get("/jobs/{master_id}/active")
async def get_active_job(master_id: str):
    """Get currently active job for master"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    active_statuses = ["assigned", "accepted", "in_transit", "in_progress"]
    
    for job in jobs_db.values():
        if job.get("master_id") == master_id and job.get("status") in active_statuses:
            return {
                "has_active_job": True,
                "job": job
            }
    
    return {
        "has_active_job": False,
        "job": None
    }


@router.post("/jobs/{master_id}/accept/{job_id}")
async def accept_job(master_id: str, job_id: str):
    """Accept an assigned job"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    
    if job.get("master_id") != master_id:
        raise HTTPException(status_code=403, detail="Job not assigned to this master")
    
    if job.get("status") != "assigned":
        raise HTTPException(status_code=400, detail=f"Cannot accept job in status: {job.get('status')}")
    
    # Update job status
    job["status"] = "accepted"
    job["accepted_at"] = datetime.utcnow().isoformat()
    _add_status_history(job, "accepted", "Master accepted the job")
    
    jobs_db[job_id] = job
    
    return {
        "success": True,
        "message": "Заказ принят",
        "job": job
    }


@router.post("/jobs/{master_id}/reject/{job_id}")
async def reject_job(master_id: str, job_id: str, reason: Optional[str] = None):
    """Reject an assigned job"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    
    if job.get("master_id") != master_id:
        raise HTTPException(status_code=403, detail="Job not assigned to this master")
    
    if job.get("status") not in ["assigned", "accepted"]:
        raise HTTPException(status_code=400, detail=f"Cannot reject job in status: {job.get('status')}")
    
    # Update job - remove master assignment
    job["status"] = "created"
    job["master_id"] = None
    job["rejection_reason"] = reason
    _add_status_history(job, "created", f"Master rejected: {reason or 'No reason provided'}")
    
    jobs_db[job_id] = job
    
    return {
        "success": True,
        "message": "Заказ отклонен, будет переназначен другому мастеру",
        "job_id": job_id
    }


@router.patch("/jobs/{master_id}/status/{job_id}")
async def update_job_status(master_id: str, job_id: str, request: JobStatusUpdate):
    """Update job status (in_transit, in_progress, completed)"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    
    if job.get("master_id") != master_id:
        raise HTTPException(status_code=403, detail="Job not assigned to this master")
    
    current_status = job.get("status")
    new_status = request.status
    
    # Validate status transition
    valid_transitions = {
        "accepted": ["in_transit", "in_progress"],
        "in_transit": ["in_progress"],
        "in_progress": ["completed"]
    }
    
    if current_status not in valid_transitions or new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {current_status} -> {new_status}"
        )
    
    # Update job
    job["status"] = new_status
    _add_status_history(job, new_status, request.note)
    
    if new_status == "in_transit":
        job["in_transit_at"] = datetime.utcnow().isoformat()
        if request.location:
            job["master_location"] = request.location
    elif new_status == "in_progress":
        job["started_at"] = datetime.utcnow().isoformat()
    elif new_status == "completed":
        job["completed_at"] = datetime.utcnow().isoformat()
    
    jobs_db[job_id] = job
    
    status_messages = {
        "in_transit": "Статус обновлен: В пути к клиенту",
        "in_progress": "Статус обновлен: Работы начаты",
        "completed": "Работа завершена. Теперь примите оплату."
    }
    
    return {
        "success": True,
        "message": status_messages.get(new_status, "Статус обновлен"),
        "job": job
    }


@router.post("/payment/process")
async def process_payment(request: PaymentProcessRequest):
    """Process payment for completed job"""
    if request.job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[request.job_id]
    
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed before payment")
    
    master_id = job.get("master_id")
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    master = masters_db[master_id]
    
    amount = request.amount or job.get("client_cost", 0)
    
    # Create transaction
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "job_id": request.job_id,
        "master_id": master_id,
        "amount": amount,
        "payment_method": request.payment_method,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Simulate payment processing
    if request.payment_method == "cash":
        # Cash payment is immediate
        transaction["status"] = "success"
        transaction["confirmed_at"] = datetime.utcnow().isoformat()
        
        # Update job
        job["status"] = "paid"
        job["paid_at"] = datetime.utcnow().isoformat()
        _add_status_history(job, "paid", f"Cash payment received: {amount} RUB")
        
        # Update master stats
        master["completed_jobs"] = master.get("completed_jobs", 0) + 1
        master["total_jobs"] = master.get("total_jobs", 0) + 1
        
        jobs_db[request.job_id] = job
        masters_db[master_id] = master
        
        result = {
            "success": True,
            "message": "Наличная оплата принята",
            "transaction": transaction,
            "master_earnings": job.get("master_earnings", 0),
            "payout_status": "Будет перечислено на ваш счет"
        }
    else:
        # Card/SBP payment - generate payment link
        transaction["payment_url"] = f"/pay/{transaction_id}"
        transaction["qr_code_url"] = f"/pay/qr/{transaction_id}"
        
        result = {
            "success": True,
            "message": "Ссылка на оплату создана",
            "transaction": transaction,
            "payment_url": transaction["payment_url"],
            "qr_code_url": transaction["qr_code_url"],
            "instructions": "Покажите QR-код клиенту или отправьте ссылку"
        }
    
    transactions_db[transaction_id] = transaction
    
    return result


@router.post("/payment/confirm/{transaction_id}")
async def confirm_payment(transaction_id: str):
    """Confirm payment (webhook simulation for card payments)"""
    if transaction_id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction = transactions_db[transaction_id]
    
    if transaction.get("status") == "success":
        return {"success": True, "message": "Payment already confirmed"}
    
    # Update transaction
    transaction["status"] = "success"
    transaction["confirmed_at"] = datetime.utcnow().isoformat()
    transactions_db[transaction_id] = transaction
    
    # Update job
    job_id = transaction.get("job_id")
    if job_id in jobs_db:
        job = jobs_db[job_id]
        job["status"] = "paid"
        job["paid_at"] = datetime.utcnow().isoformat()
        _add_status_history(job, "paid", f"Payment confirmed: {transaction.get('amount')} RUB")
        jobs_db[job_id] = job
        
        # Update master stats
        master_id = job.get("master_id")
        if master_id in masters_db:
            master = masters_db[master_id]
            master["completed_jobs"] = master.get("completed_jobs", 0) + 1
            master["total_jobs"] = master.get("total_jobs", 0) + 1
            masters_db[master_id] = master
    
    return {
        "success": True,
        "message": "Оплата подтверждена",
        "transaction": transaction
    }


@router.get("/earnings/{master_id}")
async def get_master_earnings(master_id: str, period: str = "today"):
    """Get master's earnings summary"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    master_transactions = [
        t for t in transactions_db.values()
        if t.get("master_id") == master_id and t.get("status") == "success"
    ]
    
    total_earnings = sum(
        jobs_db.get(t.get("job_id"), {}).get("master_earnings", 0)
        for t in master_transactions
    )
    
    return {
        "master_id": master_id,
        "period": period,
        "total_transactions": len(master_transactions),
        "total_earnings": total_earnings,
        "currency": "RUB",
        "recent_transactions": master_transactions[-10:]
    }


# ============= Internal Job Creation =============

@router.post("/internal/create-job")
async def create_job(request: CreateJobRequest):
    """
    Create a new job (called by AI orchestrator).
    This is an internal endpoint.
    """
    job_id = str(uuid.uuid4())
    
    job = {
        "id": job_id,
        "category": request.category,
        "client_description": request.client_description,
        "address": request.address,
        "client_cost": request.client_cost,
        "master_earnings": request.master_earnings,
        "platform_commission": request.platform_commission,
        "urgency": request.urgency,
        "client_phone": request.client_phone,
        "client_name": request.client_name,
        "instructions": request.instructions,
        "required_materials": request.required_materials,
        "media_files": request.media_files,
        "status": "created",
        "master_id": None,
        "status_history": [],
        "created_at": datetime.utcnow().isoformat()
    }
    
    jobs_db[job_id] = job
    
    return {
        "success": True,
        "job_id": job_id,
        "job": job
    }


@router.post("/internal/assign-job/{job_id}/{master_id}")
async def assign_job_to_master(job_id: str, master_id: str):
    """Assign a job to a master (called by matcher)"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    job = jobs_db[job_id]
    
    if job.get("status") != "created":
        raise HTTPException(status_code=400, detail="Job already assigned")
    
    job["master_id"] = master_id
    job["status"] = "assigned"
    job["assigned_at"] = datetime.utcnow().isoformat()
    _add_status_history(job, "assigned", f"Assigned to master {master_id}")
    
    jobs_db[job_id] = job
    
    return {
        "success": True,
        "message": "Job assigned",
        "job": job
    }


# ============= Helper Functions =============

def _add_status_history(job: Dict, new_status: str, note: str = None):
    """Add status change to job history"""
    if "status_history" not in job:
        job["status_history"] = []
    
    job["status_history"].append({
        "status": new_status,
        "timestamp": datetime.utcnow().isoformat(),
        "note": note
    })
