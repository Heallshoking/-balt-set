"""
Telegram Bot Integration for AI Service Marketplace.

This module handles:
- Telegram bot setup and configuration
- Message handling from Telegram users
- Photo/video receiving
- Interactive conversations
- Job status notifications
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ContextTypes,
        filters
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot not installed. Telegram bot functionality disabled.")

from ..services.ai_orchestrator import AIOrchestrator


logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram Bot handler for client interactions.
    
    Features:
    - Receives and processes client messages
    - Handles photo/video uploads
    - Sends AI responses
    - Manages conversation state
    - Sends job updates
    """
    
    def __init__(self, token: str, orchestrator: AIOrchestrator):
        """
        Initialize Telegram bot.
        
        Args:
            token: Telegram bot token from BotFather
            orchestrator: AI orchestrator instance
        """
        if not TELEGRAM_AVAILABLE:
            raise RuntimeError("python-telegram-bot package is required for Telegram integration")
            
        self.token = token
        self.orchestrator = orchestrator
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        welcome_message = f"""👋 Здравствуйте, {user.first_name}!

Я AI-ассистент сервиса по ремонту и обслуживанию.

🔧 Я могу помочь с:
• Электрикой (розетки, выключатели, проводка)
• Сантехникой (краны, засоры, протечки)
• Бытовой техникой (стиральные машины, холодильники)
• Мелким ремонтом

Просто опишите вашу проблему, и я:
1. Помогу определить, что нужно делать
2. Рассчитаю стоимость
3. Найду ближайшего мастера
4. Организую выезд

Напишите, что у вас случилось! 💬"""
        
        await update.message.reply_text(welcome_message)
        
        # Log new user
        logger.info(f"New user started bot: {user.id} (@{user.username})")
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """📖 Как пользоваться ботом:

1️⃣ Опишите проблему
Например: "У меня не работает розетка" или "Течет кран"

2️⃣ Отправьте фото (опционально)
Фото помогает точнее определить проблему и стоимость

3️⃣ Укажите адрес
Например: "ул. Ленина 25, кв. 10"

4️⃣ Подтвердите заказ
Я рассчитаю стоимость и найду мастера

5️⃣ Мастер свяжется с вами
И приедет в удобное время

❓ Команды:
/start - начать заново
/help - эта справка
/status - статус текущего заказа
/cancel - отменить текущий разговор

Есть вопросы? Просто напишите их! 😊"""
        
        await update.message.reply_text(help_text)
        
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user_id = str(update.effective_user.id)
        client_id = f"telegram_{user_id}"
        
        # Get conversation status
        status = self.orchestrator.get_conversation_status(client_id)
        
        if not status:
            await update.message.reply_text(
                "У вас нет активных заказов.\n\n"
                "Напишите о вашей проблеме, чтобы начать!"
            )
            return
            
        # Format status message
        stage_names = {
            "initial": "Начало разговора",
            "gathering_info": "Сбор информации",
            "confirming": "Ожидание подтверждения",
            "completed": "Завершено"
        }
        
        extracted = status["extracted_info"]
        status_text = f"""📊 Статус вашего обращения:

Этап: {stage_names.get(status['conversation_stage'], 'Неизвестно')}
Сообщений: {status['total_messages']}

📝 Собранная информация:
"""
        
        if extracted.get("problem_category"):
            category_names = {
                "electrical": "Электрика",
                "plumbing": "Сантехника",
                "appliances": "Бытовая техника",
                "renovation": "Ремонт"
            }
            status_text += f"• Категория: {category_names.get(extracted['problem_category'], 'Не определена')}\n"
            
        if extracted.get("problem_description"):
            desc = extracted["problem_description"]
            if len(desc) > 100:
                desc = desc[:100] + "..."
            status_text += f"• Описание: {desc}\n"
            
        if extracted.get("location"):
            status_text += f"• Адрес: {extracted['location']}\n"
            
        if extracted.get("urgency"):
            urgency_names = {
                "critical": "⚠️ Критическая",
                "urgent": "🔴 Срочная",
                "normal": "🟡 Обычная",
                "flexible": "🟢 Не срочная"
            }
            status_text += f"• Срочность: {urgency_names.get(extracted['urgency'], 'Не определена')}\n"
            
        await update.message.reply_text(status_text)
        
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command."""
        user_id = str(update.effective_user.id)
        client_id = f"telegram_{user_id}"
        
        # Clear conversation
        self.orchestrator.nlp.clear_conversation(client_id)
        
        await update.message.reply_text(
            "✅ Текущий разговор отменен.\n\n"
            "Если нужна помощь - просто напишите о вашей проблеме!"
        )
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages from users."""
        user = update.effective_user
        user_id = str(user.id)
        client_id = f"telegram_{user_id}"
        message_text = update.message.text
        
        logger.info(f"Message from user {user_id}: {message_text[:50]}")
        
        try:
            # Process message with AI orchestrator
            result = await self.orchestrator.handle_telegram_message(
                telegram_user_id=user_id,
                message_text=message_text,
                photos=None
            )
            
            # Send AI response
            ai_response = result.get("ai_response", "Извините, произошла ошибка. Попробуйте еще раз.")
            await update.message.reply_text(ai_response)
            
            # If quote is available, show it with buttons
            if result.get("quote"):
                await self._send_quote(update, result["quote"])
                
            # If job created, send confirmation
            if result.get("job"):
                await self._send_job_confirmation(update, result["job"])
                
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await update.message.reply_text(
                "Извините, произошла ошибка при обработке сообщения. "
                "Пожалуйста, попробуйте еще раз или обратитесь в поддержку."
            )
            
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages."""
        user = update.effective_user
        user_id = str(user.id)
        client_id = f"telegram_{user_id}"
        
        # Get photo URL (highest resolution)
        photo = update.message.photo[-1]
        file = await photo.get_file()
        photo_url = file.file_path
        
        # Get caption if present
        caption = update.message.caption or "Фото проблемы"
        
        logger.info(f"Photo from user {user_id}: {photo_url}")
        
        try:
            # Process message with photo
            result = await self.orchestrator.handle_telegram_message(
                telegram_user_id=user_id,
                message_text=caption,
                photos=[photo_url]
            )
            
            # Send AI response
            ai_response = result.get("ai_response", "Фото получено, анализирую...")
            
            # Add vision analysis summary if available
            if result.get("vision_analysis"):
                vision = result["vision_analysis"]
                if not vision.get("error"):
                    ai_response += f"\n\n🔍 Анализ фото:\n"
                    if vision.get("detected_components"):
                        ai_response += f"• Обнаружено: {', '.join(vision['detected_components'][:3])}\n"
                    if vision.get("severity"):
                        ai_response += f"• Серьезность: {vision['severity']}\n"
                        
            await update.message.reply_text(ai_response)
            
            # If quote is available, show it
            if result.get("quote"):
                await self._send_quote(update, result["quote"])
                
        except Exception as e:
            logger.error(f"Error processing photo: {e}", exc_info=True)
            await update.message.reply_text(
                "Извините, произошла ошибка при обработке фото. "
                "Попробуйте отправить еще раз."
            )
            
    async def _send_quote(self, update: Update, quote: Dict[str, Any]):
        """Send quote with confirmation buttons."""
        total = quote["cost_breakdown"]["total"]
        duration = quote["estimated_duration_hours"]
        
        quote_text = f"""💰 Расчет стоимости:

📋 Работа: {quote["solution_name"]}
⏱ Время: {duration} ч
💵 Стоимость: {total:.0f} руб.

Детали:
• Работа мастера: {quote["cost_breakdown"]["labor"]:.0f} руб.
• Материалы: {quote["cost_breakdown"]["materials"]:.0f} руб.
"""
        
        # Add urgency note
        if quote.get("urgency") == "urgent":
            quote_text += "\n⚡ Срочный выезд - мастер прибудет в течение 2-4 часов\n"
        elif quote.get("urgency") == "critical":
            quote_text += "\n🚨 Критическая ситуация - организуем экстренный выезд!\n"
            
        # Add safety notes
        if quote.get("safety_notes"):
            quote_text += "\n⚠️ Важные рекомендации:\n"
            for note in quote["safety_notes"][:2]:
                quote_text += f"• {note}\n"
                
        # Create confirmation buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтверждаю", callback_data=f"confirm_{quote['quote_id']}"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"reject_{quote['quote_id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(quote_text, reply_markup=reply_markup)
        
    async def _send_job_confirmation(self, update: Update, job: Dict[str, Any]):
        """Send job creation confirmation."""
        confirmation_text = f"""✅ Заказ создан!

📋 Номер заказа: {job['id'][:8]}
📍 Адрес: {job.get('location', 'Не указан')}
💰 Стоимость: {job['client_cost']:.0f} руб.

🔍 Ищу ближайшего мастера...

Мастер свяжется с вами в ближайшее время и согласует точное время визита.

Спасибо за обращение! 🙏"""
        
        await update.message.reply_text(confirmation_text)
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = str(query.from_user.id)
        client_id = f"telegram_{user_id}"
        
        if data.startswith("confirm_"):
            # User confirmed the quote
            quote_id = data.replace("confirm_", "")
            
            # Send confirmation message to orchestrator
            result = await self.orchestrator.process_client_message(
                client_id=client_id,
                message="Да, согласен",
                channel="telegram",
                metadata={
                    "client_name": query.from_user.first_name,
                    "telegram_username": query.from_user.username
                }
            )
            
            if result.get("job"):
                await self._send_job_confirmation(update, result["job"])
            else:
                await query.edit_message_text(
                    "✅ Принято! Пожалуйста, укажите ваш номер телефона для связи с мастером."
                )
                
        elif data.startswith("reject_"):
            # User rejected the quote
            await query.edit_message_text(
                "Понял, цена не подошла. Если передумаете или нужна другая услуга - обращайтесь!"
            )
            self.orchestrator.nlp.clear_conversation(client_id)
            
    def setup_handlers(self):
        """Set up all message and command handlers."""
        if not self.application:
            raise RuntimeError("Application not initialized")
            
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel_command))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("Telegram bot handlers configured")
        
    async def start(self):
        """Start the bot."""
        if not TELEGRAM_AVAILABLE:
            logger.error("Cannot start Telegram bot: python-telegram-bot not installed")
            return
            
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Setup handlers
        self.setup_handlers()
        
        # Start polling
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Telegram bot is running")
        
    async def stop(self):
        """Stop the bot."""
        if self.application:
            logger.info("Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")


# Factory function for easy instantiation
def create_telegram_bot(token: str, orchestrator: AIOrchestrator) -> TelegramBot:
    """
    Create and configure a Telegram bot instance.
    
    Args:
        token: Telegram bot token from BotFather
        orchestrator: AI orchestrator instance
        
    Returns:
        Configured TelegramBot instance
    """
    return TelegramBot(token=token, orchestrator=orchestrator)
