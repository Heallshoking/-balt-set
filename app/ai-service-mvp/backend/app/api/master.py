"""
Master API endpoints for onboarding and profile management.

Handles:
- Master registration (any channel)
- Profile management
- Availability/schedule management
- Terminal activation
- Job acceptance
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter()


# ============= Request/Response Models =============

class MasterRegistrationRequest(BaseModel):
    """Initial master registration request"""
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    specializations: List[str] = Field(..., min_items=1)
    experience_years: Optional[float] = 0.0
    city: str = Field(...)
    preferred_channel: str = "telegram"  # telegram, whatsapp, phone
    telegram_chat_id: Optional[str] = None


class MasterScheduleUpdate(BaseModel):
    """Schedule update request"""
    schedule: Dict[str, Dict[str, Any]]  # {monday: {available: true, start_hour: 8, end_hour: 18}}


class ServiceZone(BaseModel):
    """Service zone definition"""
    name: str
    latitude: float
    longitude: float
    radius_km: float = 10.0


class MasterProfileUpdate(BaseModel):
    """Profile update request"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    specializations: Optional[List[str]] = None
    experience_years: Optional[float] = None
    tools: Optional[List[str]] = None
    has_own_transport: Optional[str] = None
    service_zones: Optional[List[ServiceZone]] = None
    max_distance_km: Optional[float] = None


class TerminalActivationRequest(BaseModel):
    """Terminal activation request"""
    terminal_type: str = "mobile"  # mobile, physical
    device_info: Optional[Dict[str, Any]] = None


# ============= In-Memory Storage (MVP) =============
# In production: use database

masters_db: Dict[str, Dict[str, Any]] = {}


def generate_master_id() -> str:
    return str(uuid.uuid4())


# ============= API Endpoints =============

@router.post("/register")
async def register_master(request: MasterRegistrationRequest):
    """
    Register a new master.
    
    This is the entry point for master onboarding from any channel.
    After registration, master receives terminal activation instructions.
    """
    # Check if phone already registered
    for master in masters_db.values():
        if master["phone"] == request.phone:
            raise HTTPException(status_code=400, detail="Phone already registered")
    
    master_id = generate_master_id()
    
    # Create master record
    master = {
        "id": master_id,
        "full_name": request.full_name,
        "phone": request.phone,
        "email": request.email,
        "specializations": request.specializations,
        "experience_years": request.experience_years,
        "city": request.city,
        "preferred_channel": request.preferred_channel,
        "telegram_chat_id": request.telegram_chat_id,
        "status": "pending",
        "schedule": {},
        "service_zones": [],
        "tools": [],
        "has_own_transport": "no",
        "terminal_type": None,
        "terminal_activated": None,
        "rating": 0.0,
        "total_jobs": 0,
        "completed_jobs": 0,
        "created_at": datetime.utcnow().isoformat()
    }
    
    masters_db[master_id] = master
    
    # Generate terminal activation instructions
    terminal_instructions = _generate_terminal_instructions(master_id)
    
    return {
        "success": True,
        "master_id": master_id,
        "status": "pending",
        "message": "Регистрация принята. Пожалуйста, настройте расписание и активируйте терминал.",
        "next_steps": [
            "1. Укажите ваше расписание работы",
            "2. Добавьте зоны обслуживания",
            "3. Активируйте терминал для приема оплаты"
        ],
        "terminal_instructions": terminal_instructions
    }


@router.get("/{master_id}")
async def get_master_profile(master_id: str):
    """Get master profile by ID"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    return masters_db[master_id]


@router.patch("/{master_id}/profile")
async def update_master_profile(master_id: str, request: MasterProfileUpdate):
    """Update master profile"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    master = masters_db[master_id]
    
    # Update provided fields
    update_data = request.dict(exclude_unset=True)
    
    if "service_zones" in update_data:
        update_data["service_zones"] = [z.dict() if hasattr(z, 'dict') else z for z in update_data["service_zones"]]
    
    master.update(update_data)
    masters_db[master_id] = master
    
    return {
        "success": True,
        "message": "Профиль обновлен",
        "master": master
    }


@router.put("/{master_id}/schedule")
async def update_master_schedule(master_id: str, request: MasterScheduleUpdate):
    """
    Update master's work schedule.
    
    Schedule format:
    {
        "monday": {"available": true, "start_hour": 8, "end_hour": 18},
        "tuesday": {"available": true, "start_hour": 9, "end_hour": 17},
        ...
    }
    """
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    master = masters_db[master_id]
    master["schedule"] = request.schedule
    
    # If schedule is complete and terminal activated, activate master
    if _is_schedule_valid(request.schedule) and master.get("terminal_activated"):
        master["status"] = "active"
    
    masters_db[master_id] = master
    
    return {
        "success": True,
        "message": "Расписание обновлено",
        "schedule": master["schedule"],
        "status": master["status"]
    }


@router.post("/{master_id}/activate-terminal")
async def activate_terminal(master_id: str, request: TerminalActivationRequest):
    """
    Activate payment terminal for master.
    
    For mobile terminal: sends app installation link
    For physical terminal: provides pickup location
    """
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    master = masters_db[master_id]
    master["terminal_type"] = request.terminal_type
    master["terminal_activated"] = datetime.utcnow().isoformat()
    
    # If schedule is valid, activate master
    if _is_schedule_valid(master.get("schedule", {})):
        master["status"] = "active"
    
    masters_db[master_id] = master
    
    if request.terminal_type == "mobile":
        return {
            "success": True,
            "message": "Мобильный терминал активирован",
            "terminal_type": "mobile",
            "terminal_url": f"/master/terminal/{master_id}",
            "instructions": [
                "1. Откройте ссылку терминала на вашем телефоне",
                "2. Добавьте страницу на главный экран для быстрого доступа",
                "3. При получении заказа принимайте оплату через терминал"
            ],
            "master_status": master["status"]
        }
    else:
        return {
            "success": True,
            "message": "Физический терминал назначен",
            "terminal_type": "physical",
            "pickup_location": {
                "address": "ул. Примерная, д. 1",
                "working_hours": "Пн-Пт 9:00-18:00",
                "pickup_code": f"TERM-{master_id[:8].upper()}"
            },
            "master_status": master["status"]
        }


@router.get("/{master_id}/availability/today")
async def check_today_availability(master_id: str):
    """Check and confirm master's availability for today"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    master = masters_db[master_id]
    today = datetime.now().strftime("%A").lower()
    
    schedule = master.get("schedule", {})
    today_schedule = schedule.get(today, {})
    
    return {
        "master_id": master_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "day": today,
        "available": today_schedule.get("available", False),
        "hours": {
            "start": today_schedule.get("start_hour"),
            "end": today_schedule.get("end_hour")
        } if today_schedule.get("available") else None
    }


@router.post("/{master_id}/availability/confirm")
async def confirm_availability(master_id: str, available: bool, start_hour: int = 8, end_hour: int = 20):
    """Confirm or update availability for today"""
    if master_id not in masters_db:
        raise HTTPException(status_code=404, detail="Master not found")
    
    master = masters_db[master_id]
    today = datetime.now().strftime("%A").lower()
    
    if "schedule" not in master:
        master["schedule"] = {}
    
    master["schedule"][today] = {
        "available": available,
        "start_hour": start_hour,
        "end_hour": end_hour
    }
    
    masters_db[master_id] = master
    
    return {
        "success": True,
        "message": f"Доступность на сегодня {'подтверждена' if available else 'отменена'}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "schedule": master["schedule"][today]
    }


@router.get("/available/by-category/{category}")
async def get_available_masters(category: str, city: Optional[str] = None):
    """Get list of available masters for a category"""
    available_masters = []
    today = datetime.now().strftime("%A").lower()
    current_hour = datetime.now().hour
    
    for master in masters_db.values():
        # Check status
        if master.get("status") != "active":
            continue
        
        # Check specialization
        if category not in master.get("specializations", []):
            continue
        
        # Check city
        if city and master.get("city", "").lower() != city.lower():
            continue
        
        # Check today's availability
        schedule = master.get("schedule", {})
        today_schedule = schedule.get(today, {})
        
        if not today_schedule.get("available", False):
            continue
        
        start_hour = today_schedule.get("start_hour", 0)
        end_hour = today_schedule.get("end_hour", 24)
        
        if not (start_hour <= current_hour < end_hour):
            continue
        
        available_masters.append({
            "id": master["id"],
            "name": master["full_name"],
            "rating": master.get("rating", 0),
            "completed_jobs": master.get("completed_jobs", 0),
            "available_until": end_hour
        })
    
    return {
        "category": category,
        "available_count": len(available_masters),
        "masters": available_masters
    }


# ============= Helper Functions =============

def _generate_terminal_instructions(master_id: str) -> Dict[str, Any]:
    """Generate terminal activation instructions"""
    return {
        "mobile": {
            "description": "Установите терминал на ваш смартфон",
            "url": f"/master/terminal/{master_id}",
            "steps": [
                "Откройте ссылку на телефоне",
                "Добавьте на главный экран",
                "Готово! Терминал работает через браузер"
            ]
        },
        "physical": {
            "description": "Получите физический терминал",
            "pickup_info": "После активации вы получите адрес пункта выдачи"
        }
    }


def _is_schedule_valid(schedule: Dict) -> bool:
    """Check if schedule has at least one working day"""
    if not schedule:
        return False
    
    for day_schedule in schedule.values():
        if day_schedule.get("available", False):
            return True
    
    return False


# ============= List All Masters (Admin) =============

@router.get("/")
async def list_masters(status: Optional[str] = None, limit: int = 50):
    """List all masters (for admin purposes)"""
    masters = list(masters_db.values())
    
    if status:
        masters = [m for m in masters if m.get("status") == status]
    
    return {
        "total": len(masters),
        "masters": masters[:limit]
    }
