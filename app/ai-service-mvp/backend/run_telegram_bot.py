"""
Telegram Bot Startup Script.

This script starts the Telegram bot for client interactions.

Requirements:
1. Set TELEGRAM_BOT_TOKEN environment variable
2. Ensure PostgreSQL is running
3. Install all dependencies from requirements.txt

Usage:
    python run_telegram_bot.py
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.integrations.telegram_bot import create_telegram_bot, TELEGRAM_AVAILABLE
from app.services.ai_orchestrator import AIOrchestrator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('telegram_bot.log')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the Telegram bot."""
    
    # Check if Telegram package is available
    if not TELEGRAM_AVAILABLE:
        logger.error(
            "python-telegram-bot package is not installed!\n"
            "Install it with: pip install python-telegram-bot\n"
            "Or install all requirements: pip install -r requirements.txt"
        )
        sys.exit(1)
    
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        logger.error(
            "TELEGRAM_BOT_TOKEN environment variable is not set!\n"
            "Get your bot token from @BotFather on Telegram\n"
            "Then set it in your .env file:\n"
            "TELEGRAM_BOT_TOKEN=your_token_here"
        )
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("AI SERVICE MARKETPLACE - TELEGRAM BOT")
    logger.info("=" * 70)
    logger.info("")
    
    # Create AI orchestrator
    logger.info("Initializing AI Orchestrator...")
    orchestrator = AIOrchestrator()
    logger.info("✓ AI Orchestrator ready")
    logger.info("")
    
    # Create Telegram bot
    logger.info("Creating Telegram bot...")
    bot = create_telegram_bot(token=bot_token, orchestrator=orchestrator)
    logger.info("✓ Telegram bot configured")
    logger.info("")
    
    # Start bot
    logger.info("Starting Telegram bot...")
    logger.info("Bot is now running and waiting for messages...")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    try:
        await bot.start()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Received stop signal...")
        await bot.stop()
        logger.info("Bot stopped successfully")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        if bot.application:
            await bot.stop()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
