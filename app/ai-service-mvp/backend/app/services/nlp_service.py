"""
NLP Service for AI-powered conversational interactions.

This module handles:
- Speech-to-text conversion for phone calls
- Text-to-speech for AI responses
- Intent recognition from client messages
- Natural language understanding
- Dialogue management
- Response generation
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import re
from datetime import datetime


class IntentType(Enum):
    """Types of user intents we can recognize."""
    REQUEST_SERVICE = "request_service"
    DESCRIBE_PROBLEM = "describe_problem"
    PROVIDE_LOCATION = "provide_location"
    CONFIRM_PRICE = "confirm_price"
    REJECT_PRICE = "reject_price"
    REQUEST_TIMING = "request_timing"
    CONFIRM_TIMING = "confirm_timing"
    URGENT_REQUEST = "urgent_request"
    QUESTION = "question"
    GREETING = "greeting"
    GRATITUDE = "gratitude"
    UNKNOWN = "unknown"


class UrgencyLevel(Enum):
    """Urgency levels extracted from messages."""
    CRITICAL = "critical"  # Immediate danger, requires instant response
    URGENT = "urgent"      # Same day service needed
    NORMAL = "normal"      # Within 1-3 days
    FLEXIBLE = "flexible"  # Client is flexible on timing


class ConversationContext:
    """Maintains context during a conversation."""
    
    def __init__(self, client_id: str, channel: str):
        self.client_id = client_id
        self.channel = channel  # telegram, phone, whatsapp, web_form
        self.messages: List[Dict[str, Any]] = []
        self.extracted_info: Dict[str, Any] = {
            "problem_category": None,
            "problem_description": None,
            "location": None,
            "urgency": UrgencyLevel.NORMAL.value,
            "preferred_timing": None,
            "media_files": [],
            "client_name": None,
            "client_phone": None,
        }
        self.current_intent: Optional[IntentType] = None
        self.missing_info: List[str] = []
        self.conversation_stage: str = "initial"  # initial, gathering_info, confirming, completed
        
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history."""
        self.messages.append({
            "role": role,  # "client" or "ai"
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })
        
    def update_extracted_info(self, key: str, value: Any):
        """Update extracted information."""
        self.extracted_info[key] = value
        
    def is_info_complete(self) -> bool:
        """Check if we have all necessary information."""
        required_fields = ["problem_category", "problem_description", "location"]
        return all(self.extracted_info.get(field) for field in required_fields)


class NLPService:
    """
    Natural Language Processing service for conversational AI.
    
    In production, this would integrate with services like:
    - OpenAI GPT-4 for understanding and generation
    - Google Cloud Speech-to-Text / Yandex SpeechKit
    - Yandex SpeechKit for Russian language
    
    For MVP, we use rule-based approaches with keyword matching.
    """
    
    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}
        
        # Keywords for intent recognition (Russian language)
        self.intent_keywords = {
            IntentType.REQUEST_SERVICE: [
                "нужен", "требуется", "вызов", "приезжайте", "помогите",
                "сделайте", "отремонтируйте", "почините", "установите"
            ],
            IntentType.DESCRIBE_PROBLEM: [
                "не работает", "сломал", "перестал", "искрит", "течет",
                "протечка", "выбивает", "горит", "запах", "треснул",
                "засор", "забился", "отвалил", "оторвался"
            ],
            IntentType.URGENT_REQUEST: [
                "срочно", "прямо сейчас", "немедленно", "горит", "течет",
                "искрит", "опасно", "сегодня", "быстрее", "аварийно"
            ],
            IntentType.CONFIRM_PRICE: [
                "да", "согласен", "подходит", "хорошо", "договорились",
                "записывайте", "оформляйте", "принято", "ок", "окей"
            ],
            IntentType.REJECT_PRICE: [
                "дорого", "нет", "не подходит", "не устраивает", "отказ",
                "много", "откажусь", "передумал"
            ],
            IntentType.GREETING: [
                "здравствуйте", "привет", "добрый день", "добрый вечер",
                "доброе утро", "слушаю"
            ],
            IntentType.GRATITUDE: [
                "спасибо", "благодарю", "отлично", "замечательно", "супер"
            ]
        }
        
        # Problem category keywords
        self.category_keywords = {
            "electrical": [
                "розетка", "выключатель", "свет", "электри", "провод",
                "автомат", "щиток", "лампочка", "светильник", "люстра",
                "короткое замыкание", "проводка"
            ],
            "plumbing": [
                "вода", "кран", "труба", "сантехник", "унитаз", "ванна",
                "раковина", "течь", "протечка", "засор", "канализация",
                "смеситель", "душ"
            ],
            "appliances": [
                "стиральная машина", "холодильник", "посудомоечная",
                "плита", "духовка", "микроволновка", "бойлер", "водонагреватель"
            ],
            "renovation": [
                "покраска", "обои", "пол", "потолок", "плитка", "ламинат",
                "шпаклевка", "штукатурка", "отделка"
            ]
        }
        
        # Urgency keywords
        self.urgency_keywords = {
            UrgencyLevel.CRITICAL: [
                "искрит", "горит", "дым", "запах горелого", "удар током",
                "вода течет", "затопление", "прорвало", "фонтан"
            ],
            UrgencyLevel.URGENT: [
                "срочно", "сегодня", "как можно скорее", "прямо сейчас",
                "немедленно", "быстро"
            ],
            UrgencyLevel.FLEXIBLE: [
                "когда удобно", "не срочно", "можно подождать", "в течение недели"
            ]
        }
        
    def speech_to_text(self, audio_data: bytes, language: str = "ru-RU") -> str:
        """
        Convert speech audio to text.
        
        In production: integrate with Yandex SpeechKit or Google Cloud Speech-to-Text
        For MVP: placeholder returning mock transcription
        """
        # TODO: Integrate with Yandex SpeechKit API
        # https://cloud.yandex.ru/docs/speechkit/
        
        # Placeholder implementation
        return "Transcribed text would be here"
        
    def text_to_speech(self, text: str, language: str = "ru-RU") -> bytes:
        """
        Convert text to speech audio.
        
        In production: integrate with Yandex SpeechKit or Google Cloud Text-to-Speech
        For MVP: placeholder returning empty bytes
        """
        # TODO: Integrate with Yandex SpeechKit API for TTS
        
        # Placeholder implementation
        return b""
        
    def recognize_intent(self, message: str, context: ConversationContext) -> IntentType:
        """
        Recognize user intent from message.
        
        Uses keyword matching for MVP. In production, would use ML models.
        """
        message_lower = message.lower()
        
        # Check each intent type
        intent_scores: Dict[IntentType, int] = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score
                
        if intent_scores:
            # Return intent with highest score
            return max(intent_scores, key=intent_scores.get)
            
        # Default to unknown
        return IntentType.UNKNOWN
        
    def extract_problem_category(self, message: str) -> Optional[str]:
        """Extract problem category from message."""
        message_lower = message.lower()
        
        category_scores: Dict[str, int] = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                category_scores[category] = score
                
        if category_scores:
            return max(category_scores, key=category_scores.get)
            
        return None
        
    def extract_urgency(self, message: str) -> UrgencyLevel:
        """Extract urgency level from message."""
        message_lower = message.lower()
        
        # Check critical first
        if any(keyword in message_lower for keyword in self.urgency_keywords[UrgencyLevel.CRITICAL]):
            return UrgencyLevel.CRITICAL
            
        # Then urgent
        if any(keyword in message_lower for keyword in self.urgency_keywords[UrgencyLevel.URGENT]):
            return UrgencyLevel.URGENT
            
        # Then flexible
        if any(keyword in message_lower for keyword in self.urgency_keywords[UrgencyLevel.FLEXIBLE]):
            return UrgencyLevel.FLEXIBLE
            
        # Default to normal
        return UrgencyLevel.NORMAL
        
    def extract_location(self, message: str) -> Optional[str]:
        """
        Extract address/location from message.
        
        In production: use Named Entity Recognition (NER) for addresses
        For MVP: simple pattern matching
        """
        # Look for address patterns
        # Example: "улица Ленина 25", "ул. Пушкина, д. 10, кв. 5"
        
        address_patterns = [
            r'(?:ул(?:ица)?\.?\s+[\w\-]+\s+\d+)',
            r'(?:проспект\s+[\w\-]+\s+\d+)',
            r'(?:пер(?:еулок)?\.?\s+[\w\-]+\s+\d+)',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(0)
                
        return None
        
    def extract_phone(self, message: str) -> Optional[str]:
        """Extract phone number from message."""
        # Russian phone patterns: +7, 8, with various formats
        phone_patterns = [
            r'\+7[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
            r'8[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
            r'\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, message)
            if match:
                # Normalize phone number
                phone = re.sub(r'[\s\-]', '', match.group(0))
                if phone.startswith('8'):
                    phone = '+7' + phone[1:]
                elif not phone.startswith('+'):
                    phone = '+7' + phone
                return phone
                
        return None
        
    def process_message(
        self,
        client_id: str,
        message: str,
        channel: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a client message and generate appropriate response.
        
        Args:
            client_id: Unique identifier for the client
            message: The message text from client
            channel: Communication channel (telegram, phone, whatsapp, etc.)
            media_urls: Optional list of media file URLs (photos, videos)
            
        Returns:
            Dictionary containing:
            - response: AI generated response
            - intent: Recognized intent
            - extracted_info: Information extracted from message
            - next_action: What should happen next
            - conversation_complete: Whether conversation has all needed info
        """
        # Get or create conversation context
        if client_id not in self.conversations:
            self.conversations[client_id] = ConversationContext(client_id, channel)
            
        context = self.conversations[client_id]
        
        # Add message to history
        context.add_message("client", message, {"media_urls": media_urls})
        
        # Recognize intent
        intent = self.recognize_intent(message, context)
        context.current_intent = intent
        
        # Extract information
        extracted_info = {}
        
        # Extract problem category if not already known
        if not context.extracted_info["problem_category"]:
            category = self.extract_problem_category(message)
            if category:
                context.update_extracted_info("problem_category", category)
                extracted_info["problem_category"] = category
                
        # Extract urgency
        urgency = self.extract_urgency(message)
        context.update_extracted_info("urgency", urgency.value)
        extracted_info["urgency"] = urgency.value
        
        # Extract location
        location = self.extract_location(message)
        if location:
            context.update_extracted_info("location", location)
            extracted_info["location"] = location
            
        # Extract phone
        phone = self.extract_phone(message)
        if phone:
            context.update_extracted_info("client_phone", phone)
            extracted_info["client_phone"] = phone
            
        # Update problem description
        if intent in [IntentType.DESCRIBE_PROBLEM, IntentType.REQUEST_SERVICE]:
            current_desc = context.extracted_info.get("problem_description", "")
            if current_desc:
                context.update_extracted_info("problem_description", f"{current_desc} {message}")
            else:
                context.update_extracted_info("problem_description", message)
            extracted_info["problem_description"] = context.extracted_info["problem_description"]
            
        # Add media files to context
        if media_urls:
            context.extracted_info["media_files"].extend(media_urls)
            extracted_info["media_files"] = media_urls
            
        # Generate response based on intent and context
        response = self._generate_response(intent, context)
        
        # Add AI response to history
        context.add_message("ai", response)
        
        # Determine next action
        next_action = self._determine_next_action(context)
        
        return {
            "response": response,
            "intent": intent.value,
            "extracted_info": extracted_info,
            "all_extracted_info": context.extracted_info,
            "next_action": next_action,
            "conversation_complete": context.is_info_complete(),
            "conversation_stage": context.conversation_stage
        }
        
    def _generate_response(self, intent: IntentType, context: ConversationContext) -> str:
        """
        Generate appropriate AI response based on intent and context.
        
        In production: use GPT-4 or similar for more natural responses
        For MVP: template-based responses
        """
        # Greeting
        if intent == IntentType.GREETING:
            if context.channel == "phone":
                return "Здравствуйте, это автоматизированная система сервиса. Чем могу помочь?"
            else:
                return "Здравствуйте! Я помогу вам решить вашу проблему. Опишите, что случилось."
                
        # Request service or describe problem
        if intent in [IntentType.REQUEST_SERVICE, IntentType.DESCRIBE_PROBLEM]:
            if not context.extracted_info["problem_category"]:
                return "Понял, у вас есть проблема. Можете описать подробнее? Что именно не работает?"
            else:
                category = context.extracted_info["problem_category"]
                category_names = {
                    "electrical": "электрикой",
                    "plumbing": "сантехникой",
                    "appliances": "бытовой техникой",
                    "renovation": "ремонтом"
                }
                category_name = category_names.get(category, "проблемой")
                
                # Check what info is missing
                if not context.extracted_info["location"]:
                    return f"Понял, проблема с {category_name}. Какой у вас адрес?"
                    
                if not context.extracted_info["problem_description"] or len(context.extracted_info["problem_description"]) < 20:
                    return "Не могли бы вы описать проблему более подробно? Это поможет точнее оценить работу."
                    
                # Check if we need photos
                if not context.extracted_info["media_files"] and category in ["electrical", "plumbing"]:
                    return "Не могли бы вы прислать фото проблемного участка? Это поможет точнее определить стоимость."
                    
                return "Отлично, у меня достаточно информации. Сейчас рассчитаю стоимость и подберу мастера."
                
        # Urgent request
        if intent == IntentType.URGENT_REQUEST:
            urgency = context.extracted_info.get("urgency", UrgencyLevel.NORMAL.value)
            if urgency == UrgencyLevel.CRITICAL.value:
                return "Понимаю, ситуация критическая. Сейчас найду ближайшего доступного мастера для срочного выезда."
            else:
                return "Постараемся организовать выезд как можно скорее. Когда вам удобно?"
                
        # Confirm price
        if intent == IntentType.CONFIRM_PRICE:
            context.conversation_stage = "completed"
            return "Отлично! Мастер получит ваш заказ и свяжется с вами в ближайшее время. Спасибо!"
            
        # Reject price
        if intent == IntentType.REJECT_PRICE:
            context.conversation_stage = "completed"
            return "Понимаю. Если передумаете или нужна будет помощь - обращайтесь!"
            
        # Gratitude
        if intent == IntentType.GRATITUDE:
            return "Всегда рад помочь! Если будут еще вопросы - обращайтесь."
            
        # Default response
        return "Я понял ваше сообщение. Можете уточнить детали?"
        
    def _determine_next_action(self, context: ConversationContext) -> str:
        """Determine what action should be taken next."""
        # If conversation is complete, create job
        if context.is_info_complete():
            if context.conversation_stage == "completed":
                return "create_job"
            else:
                return "calculate_price"
                
        # If critical urgency, prioritize
        if context.extracted_info.get("urgency") == UrgencyLevel.CRITICAL.value:
            return "escalate_to_urgent"
            
        # If we have category and description but no location
        if context.extracted_info["problem_category"] and context.extracted_info["problem_description"]:
            if not context.extracted_info["location"]:
                return "request_location"
                
        # Continue gathering information
        return "continue_conversation"
        
    def get_conversation_summary(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of the conversation for job creation."""
        if client_id not in self.conversations:
            return None
            
        context = self.conversations[client_id]
        
        return {
            "client_id": client_id,
            "channel": context.channel,
            "extracted_info": context.extracted_info,
            "message_history": context.messages,
            "total_messages": len(context.messages),
            "conversation_stage": context.conversation_stage,
            "is_complete": context.is_info_complete()
        }
        
    def clear_conversation(self, client_id: str):
        """Clear conversation context after job is created."""
        if client_id in self.conversations:
            del self.conversations[client_id]
