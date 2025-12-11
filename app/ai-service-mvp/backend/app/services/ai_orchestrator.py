"""
AI Orchestrator - coordinates all AI services to process client requests.

This module:
- Receives requests from multiple channels (phone, Telegram, web forms)
- Coordinates NLP, Vision, and Knowledge Base services
- Manages conversation flow
- Generates cost estimates
- Creates job records
- Assigns jobs to masters
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import uuid

from .nlp_service import NLPService, IntentType, UrgencyLevel
from .vision_service import VisionService, ProblemSeverity
from .knowledge_base import KnowledgeBase, SkillLevel
from .pricing_engine import PricingEngine
from .master_matcher import MasterMatcher


class AIOrchestrator:
    """
    Main orchestrator that coordinates all AI services.
    
    Handles the complete flow:
    1. Receive client request (any channel)
    2. Process with NLP
    3. Analyze images if provided
    4. Match problem to knowledge base
    5. Calculate pricing
    6. Find and assign master
    7. Create job record
    """
    
    def __init__(self):
        self.nlp = NLPService()
        self.vision = VisionService()
        self.knowledge = KnowledgeBase()
        self.pricing = PricingEngine()
        # Для MVP мы не используем MasterMatcher (требует БД)
        # Вместо этого используем _auto_assign_master
        self.master_matcher = None
        
        # Track active conversations
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        
    async def process_client_message(
        self,
        client_id: str,
        message: str,
        channel: str,
        media_urls: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a message from a client.
        
        Args:
            client_id: Unique client identifier
            message: The message text
            channel: Communication channel (telegram, phone, whatsapp, web_form)
            media_urls: Optional photos/videos
            metadata: Additional context (client name, phone, etc.)
            
        Returns:
            Response with AI reply and next actions
        """
        # Step 1: Process message with NLP
        nlp_result = self.nlp.process_message(
            client_id=client_id,
            message=message,
            channel=channel,
            media_urls=media_urls
        )
        
        # Step 2: Analyze images if provided
        vision_result = None
        if media_urls:
            vision_context = {
                "category": nlp_result["all_extracted_info"].get("problem_category"),
                "description": nlp_result["all_extracted_info"].get("problem_description", "")
            }
            vision_result = self.vision.analyze_images(media_urls, vision_context)
            
            # Update extracted info with vision analysis
            if vision_result and not vision_result.get("error"):
                # Use vision analysis to enhance problem understanding
                if not nlp_result["all_extracted_info"].get("problem_category"):
                    nlp_result["all_extracted_info"]["problem_category"] = vision_result["primary_category"]
                    
                # Add severity info
                nlp_result["all_extracted_info"]["severity"] = vision_result["severity"]
                nlp_result["all_extracted_info"]["safety_hazards"] = vision_result["safety_hazards"]
                
        # Step 3: Check if we have enough information to proceed
        conversation_summary = self.nlp.get_conversation_summary(client_id)
        
        response = {
            "client_id": client_id,
            "ai_response": nlp_result["response"],
            "intent": nlp_result["intent"],
            "extracted_info": nlp_result["all_extracted_info"],
            "vision_analysis": vision_result,
            "next_action": nlp_result["next_action"],
            "conversation_complete": nlp_result["conversation_complete"]
        }
        
        # Step 4: If conversation is complete, generate quote
        if nlp_result["conversation_complete"] and nlp_result["next_action"] == "calculate_price":
            quote = await self._generate_quote(conversation_summary)
            response["quote"] = quote
            response["ai_response"] = self._format_quote_message(quote)
            response["next_action"] = "awaiting_confirmation"
            
        # Step 5: If client confirmed, create job and assign master
        if nlp_result["intent"] == IntentType.CONFIRM_PRICE.value:
            job = await self._create_and_assign_job(client_id, conversation_summary, metadata)
            response["job"] = job
            response["next_action"] = "job_created"
            
        return response
        
    async def _generate_quote(self, conversation_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a price quote for the job."""
        extracted_info = conversation_summary["extracted_info"]
        
        # Find matching solution in knowledge base
        solution = self.knowledge.find_solution(
            problem_description=extracted_info.get("problem_description", ""),
            category=extracted_info.get("problem_category")
        )
        
        # Determine complexity
        complexity = "medium"
        if solution:
            if solution.skill_level == SkillLevel.BASIC:
                complexity = "simple"
            elif solution.skill_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]:
                complexity = "complex"
                
        # Get estimated hours
        estimated_hours = solution.estimated_time_hours if solution else 1.5
        
        # Prepare materials list
        required_materials = solution.required_materials if solution else []
        
        # Calculate cost
        cost_breakdown = self.pricing.calculate_job_cost(
            category=extracted_info.get("problem_category", "electrical"),
            problem_description=extracted_info.get("problem_description", ""),
            complexity=complexity,
            estimated_hours=estimated_hours,
            required_materials=required_materials
        )
        
        quote = {
            "problem_category": extracted_info.get("problem_category"),
            "problem_description": extracted_info.get("problem_description"),
            "solution_name": solution.problem_name if solution else "Диагностика и ремонт",
            "estimated_duration_hours": estimated_hours,
            "complexity": complexity,
            "cost_breakdown": {
                "labor": float(cost_breakdown["labor_cost"]),
                "materials": float(cost_breakdown["materials_cost"]),
                "subtotal": float(cost_breakdown["subtotal"]),
                "total": float(cost_breakdown["total_cost"])
            },
            "urgency": extracted_info.get("urgency", "normal"),
            "safety_notes": solution.safety_precautions[:3] if solution else [],
            "quote_id": str(uuid.uuid4()),
            "valid_until": (datetime.utcnow().replace(hour=23, minute=59, second=59)).isoformat()
        }
        
        return quote
        
    def _format_quote_message(self, quote: Dict[str, Any]) -> str:
        """Format a quote into a user-friendly message."""
        total = quote["cost_breakdown"]["total"]
        duration = quote["estimated_duration_hours"]
        
        message = f"""Подобрал решение для вашей проблемы:

📋 Работа: {quote["solution_name"]}
⏱ Время выполнения: {duration} ч
💰 Стоимость: {total:.0f} руб.

Разбивка стоимости:
• Работа мастера: {quote["cost_breakdown"]["labor"]:.0f} руб.
• Материалы: {quote["cost_breakdown"]["materials"]:.0f} руб.
"""
        
        if quote.get("urgency") == UrgencyLevel.URGENT.value:
            message += "\n⚡ Срочный выезд - мастер прибудет в течение 2-4 часов"
        elif quote.get("urgency") == UrgencyLevel.CRITICAL.value:
            message += "\n🚨 Критическая ситуация - организуем экстренный выезд!"
            
        if quote.get("safety_notes"):
            message += f"\n\n⚠️ Важно:\n"
            for note in quote["safety_notes"]:
                message += f"• {note}\n"
                
        message += "\nПодтверждаете заказ?"
        
        return message
        
    async def _create_and_assign_job(
        self,
        client_id: str,
        conversation_summary: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create job record and assign to a master."""
        extracted_info = conversation_summary["extracted_info"]
        
        # Find solution
        solution = self.knowledge.find_solution(
            problem_description=extracted_info.get("problem_description", ""),
            category=extracted_info.get("problem_category")
        )
        
        # Calculate pricing
        complexity = "medium"
        if solution:
            if solution.skill_level == SkillLevel.BASIC:
                complexity = "simple"
            elif solution.skill_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]:
                complexity = "complex"
                
        estimated_hours = solution.estimated_time_hours if solution else 1.5
        required_materials = solution.required_materials if solution else []
        
        cost_breakdown = self.pricing.calculate_job_cost(
            category=extracted_info.get("problem_category", "electrical"),
            problem_description=extracted_info.get("problem_description", ""),
            complexity=complexity,
            estimated_hours=estimated_hours,
            required_materials=required_materials
        )
        
        # Generate job instructions
        job_instructions = None
        if solution:
            job_instructions = self.knowledge.generate_job_instructions(
                solution=solution,
                client_specifics={
                    "notes": extracted_info.get("problem_description"),
                    "urgency": extracted_info.get("urgency", "normal"),
                    "media_files": extracted_info.get("media_files", [])
                }
            )
            
        # Create job record (in production: save to database)
        job = {
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "client_name": metadata.get("client_name") if metadata else None,
            "client_phone": extracted_info.get("client_phone") or (metadata.get("client_phone") if metadata else None),
            "category": extracted_info.get("problem_category"),
            "problem_description": extracted_info.get("problem_description"),
            "location": extracted_info.get("location"),
            "media_files": extracted_info.get("media_files", []),
            "urgency": extracted_info.get("urgency", "normal"),
            "client_cost": float(cost_breakdown["total_cost"]),
            "master_earnings": float(cost_breakdown["master_earnings"]),
            "platform_commission": float(cost_breakdown["platform_commission"]),
            "estimated_hours": estimated_hours,
            "complexity": complexity,
            "instructions": job_instructions,
            "required_materials": required_materials,
            "conversation_history": conversation_summary["message_history"],
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "channel": conversation_summary["channel"]
        }
        
        # AUTO-ASSIGN TO MASTER
        assigned_master = await self._auto_assign_master(job)
        
        if assigned_master:
            job["master_id"] = assigned_master["id"]
            job["status"] = "assigned"
            job["assigned_at"] = datetime.utcnow().isoformat()
            job["master_assignment_status"] = "assigned"
            
            # Сохранить заказ в базу terminal API
            await self._save_job_to_terminal(job)
        else:
            job["master_assignment_status"] = "no_masters_available"
        
        # Clear conversation
        self.nlp.clear_conversation(client_id)
        
        return job
    
    async def _auto_assign_master(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Автоматически подобрать и назначить мастера для заказа."""
        from datetime import datetime
        
        # Import masters database from master.py API
        try:
            from app.api.master import masters_db
        except ImportError:
            return None
        
        category = job.get("category")
        urgency = job.get("urgency", "normal")
        
        # Получить текущее время
        now = datetime.now()
        current_day = now.strftime("%A").lower()
        current_hour = now.hour
        
        # Найти подходящих мастеров
        suitable_masters = []
        
        for master_id, master in masters_db.items():
            # Проверка статуса
            if master.get("status") != "active":
                continue
            
            # Проверка специализации
            if category not in master.get("specializations", []):
                continue
            
            # Проверка доступности на сегодня
            schedule = master.get("schedule", {})
            today_schedule = schedule.get(current_day, {})
            
            if not today_schedule.get("available", False):
                continue
            
            start_hour = today_schedule.get("start_hour", 0)
            end_hour = today_schedule.get("end_hour", 24)
            
            # Проверка, что мастер сейчас работает
            if not (start_hour <= current_hour < end_hour):
                continue
            
            # Рассчитать рейтинг мастера
            rating = master.get("rating", 0)
            completed_jobs = master.get("completed_jobs", 0)
            
            # Бонус за срочность
            score = rating * 10 + completed_jobs
            
            suitable_masters.append({
                "id": master_id,
                "master": master,
                "score": score
            })
        
        if not suitable_masters:
            return None
        
        # Сортировка по рейтингу (лучшие мастера первыми)
        suitable_masters.sort(key=lambda x: x["score"], reverse=True)
        
        # Выбрать лучшего мастера
        best_match = suitable_masters[0]
        
        return {
            "id": best_match["id"],
            "name": best_match["master"]["full_name"],
            "rating": best_match["master"]["rating"],
            "phone": best_match["master"]["phone"]
        }
    
    async def _save_job_to_terminal(self, job: Dict[str, Any]):
        """Сохранить заказ в базу terminal API чтобы мастер его увидел."""
        try:
            from app.api.terminal import jobs_db
            jobs_db[job["id"]] = job
        except ImportError:
            pass
        
    async def handle_phone_call(
        self,
        phone_number: str,
        audio_stream: Any
    ) -> Dict[str, Any]:
        """
        Handle incoming phone call with real-time conversation.
        
        In production: integrate with telephony provider
        Uses speech-to-text and text-to-speech for real-time interaction
        """
        # Generate unique client ID from phone
        client_id = f"phone_{phone_number}"
        
        # In production:
        # 1. Use speech-to-text to transcribe caller
        # 2. Process with NLP
        # 3. Generate response
        # 4. Use text-to-speech to respond
        # 5. Continue conversation loop
        
        return {
            "client_id": client_id,
            "channel": "phone",
            "status": "active_call",
            "message": "Phone integration requires telephony provider setup"
        }
        
    async def handle_telegram_message(
        self,
        telegram_user_id: str,
        message_text: str,
        photos: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Handle message from Telegram bot."""
        client_id = f"telegram_{telegram_user_id}"
        
        result = await self.process_client_message(
            client_id=client_id,
            message=message_text,
            channel="telegram",
            media_urls=photos
        )
        
        return result
        
    async def handle_web_form(
        self,
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle submission from web form."""
        # Extract data from form
        client_id = f"web_{form_data.get('email', str(uuid.uuid4()))}"
        
        # Construct message from form fields
        message = f"""Проблема: {form_data.get('problem_description', '')}
Категория: {form_data.get('category', '')}
Адрес: {form_data.get('address', '')}
Предпочтительное время: {form_data.get('preferred_time', '')}"""
        
        metadata = {
            "client_name": form_data.get("name"),
            "client_phone": form_data.get("phone"),
            "client_email": form_data.get("email")
        }
        
        result = await self.process_client_message(
            client_id=client_id,
            message=message,
            channel="web_form",
            media_urls=form_data.get("photos"),
            metadata=metadata
        )
        
        return result
        
    def get_active_conversations_count(self) -> int:
        """Get count of active conversations."""
        return len([c for c in self.nlp.conversations.values() 
                   if c.conversation_stage != "completed"])
        
    def get_conversation_status(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific conversation."""
        return self.nlp.get_conversation_summary(client_id)
