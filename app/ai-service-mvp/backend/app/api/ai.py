"""
AI API endpoints for client interactions.

Handles:
- Message processing from multiple channels
- Quote generation
- Job creation
- Conversation management
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..services.ai_orchestrator import AIOrchestrator


router = APIRouter()
orchestrator = AIOrchestrator()


# Request/Response Models
class MessageRequest(BaseModel):
    """Request model for processing a client message."""
    client_id: str = Field(..., description="Unique client identifier")
    message: str = Field(..., description="Message text from client")
    channel: str = Field(..., description="Communication channel (telegram, phone, whatsapp, web_form)")
    media_urls: Optional[List[str]] = Field(None, description="URLs of attached photos/videos")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (name, phone, etc.)")


class MessageResponse(BaseModel):
    """Response model for processed message."""
    client_id: str
    ai_response: str
    intent: str
    extracted_info: Dict[str, Any]
    vision_analysis: Optional[Dict[str, Any]] = None
    quote: Optional[Dict[str, Any]] = None
    job: Optional[Dict[str, Any]] = None
    next_action: str
    conversation_complete: bool


class TelegramMessageRequest(BaseModel):
    """Request from Telegram bot."""
    telegram_user_id: str
    message_text: str
    photos: Optional[List[str]] = None
    user_name: Optional[str] = None


class WebFormRequest(BaseModel):
    """Request from web form."""
    name: str
    phone: str
    email: Optional[str] = None
    category: str
    problem_description: str
    address: str
    preferred_time: Optional[str] = None
    photos: Optional[List[str]] = None


@router.post("/messages", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """
    Process a message from any channel.
    
    This is the main endpoint for AI-powered conversation.
    """
    try:
        result = await orchestrator.process_client_message(
            client_id=request.client_id,
            message=request.message,
            channel=request.channel,
            media_urls=request.media_urls,
            metadata=request.metadata
        )
        
        return MessageResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.post("/telegram/message")
async def handle_telegram_message(request: TelegramMessageRequest):
    """Handle incoming message from Telegram bot."""
    try:
        result = await orchestrator.handle_telegram_message(
            telegram_user_id=request.telegram_user_id,
            message_text=request.message_text,
            photos=request.photos
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling Telegram message: {str(e)}")


@router.post("/web-form")
async def handle_web_form(request: WebFormRequest):
    """Handle submission from web form."""
    try:
        form_data = request.dict()
        result = await orchestrator.handle_web_form(form_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling web form: {str(e)}")


@router.get("/conversations/active")
async def get_active_conversations():
    """Get count of active conversations."""
    try:
        count = orchestrator.get_active_conversations_count()
        return {
            "active_conversations": count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversations: {str(e)}")


@router.get("/conversations/{client_id}")
async def get_conversation_status(client_id: str):
    """Get status of a specific conversation."""
    try:
        status = orchestrator.get_conversation_status(client_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation: {str(e)}")


@router.post("/analyze/image")
async def analyze_image(
    image_url: str = Form(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Analyze a single image to identify problems.
    
    Useful for direct image analysis without full conversation.
    """
    try:
        context = {}
        if category:
            context["category"] = category
        if description:
            context["description"] = description
            
        result = orchestrator.vision.analyze_image(image_url, context)
        
        return result.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


@router.post("/analyze/images")
async def analyze_images(
    image_urls: List[str],
    category: Optional[str] = None,
    description: Optional[str] = None
):
    """Analyze multiple images."""
    try:
        context = {}
        if category:
            context["category"] = category
        if description:
            context["description"] = description
            
        result = orchestrator.vision.analyze_images(image_urls, context)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing images: {str(e)}")


@router.get("/knowledge/solutions")
async def get_solutions(category: Optional[str] = None):
    """Get available solutions from knowledge base."""
    try:
        if category:
            solutions = orchestrator.knowledge.get_solutions_by_category(category)
        else:
            solutions = list(orchestrator.knowledge.solutions.values())
            
        return {
            "total": len(solutions),
            "solutions": [s.to_dict() for s in solutions]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting solutions: {str(e)}")


@router.get("/knowledge/solutions/{problem_id}")
async def get_solution(problem_id: str):
    """Get a specific solution by ID."""
    try:
        solution = orchestrator.knowledge.get_solution_by_id(problem_id)
        
        if not solution:
            raise HTTPException(status_code=404, detail="Solution not found")
            
        return solution.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting solution: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for AI services."""
    return {
        "status": "healthy",
        "services": {
            "nlp": "operational",
            "vision": "operational",
            "knowledge_base": "operational",
            "pricing": "operational",
            "master_matcher": "operational"
        },
        "active_conversations": orchestrator.get_active_conversations_count(),
        "timestamp": datetime.utcnow().isoformat()
    }
