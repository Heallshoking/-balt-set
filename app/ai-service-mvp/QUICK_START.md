# Quick Start Guide - AI Service Marketplace MVP

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- Basic understanding of REST APIs

## Installation (5 minutes)

### 1. Navigate to Backend Directory

```bash
cd ai-service-mvp/backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Expected packages:
- FastAPI (web framework)
- Pydantic (data validation)
- AsyncPG (PostgreSQL driver)
- And 20+ other packages

### 4. Set Up Database

Create PostgreSQL database:
```bash
createdb ai_service
```

Apply schema:
```bash
psql -d ai_service -f ../database/schema.sql
```

### 5. Configure Environment

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/ai_service

# Platform Configuration
PLATFORM_COMMISSION_RATE=0.25
MINIMUM_JOB_COST=500.0
MAXIMUM_JOB_COST=50000.0

# YooKassa (for payments)
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# CORS (for web clients)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### 6. Start the Server

```bash
uvicorn main:app --reload
```

Server will start on: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Quick Test

### Test 1: Health Check

```bash
curl http://localhost:8000/api/v1/ai/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "nlp": "operational",
    "vision": "operational",
    "knowledge_base": "operational",
    "pricing": "operational",
    "master_matcher": "operational"
  },
  "active_conversations": 0
}
```

### Test 2: Process a Message

```bash
curl -X POST "http://localhost:8000/api/v1/ai/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test_001",
    "message": "У меня не работает розетка",
    "channel": "telegram"
  }'
```

Expected response:
```json
{
  "client_id": "test_001",
  "ai_response": "Понял, у вас проблема с розеткой. Какой у вас адрес?",
  "intent": "describe_problem",
  "extracted_info": {
    "problem_category": "electrical",
    "urgency": "normal",
    "problem_description": "У меня не работает розетка"
  },
  "next_action": "continue_conversation",
  "conversation_complete": false
}
```

### Test 3: Get Knowledge Base Solutions

```bash
curl "http://localhost:8000/api/v1/ai/knowledge/solutions?category=electrical"
```

You'll get a list of electrical repair solutions with full details.

## Using the API

### Complete Conversation Flow

#### Step 1: Initial Message
```bash
curl -X POST "http://localhost:8000/api/v1/ai/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_123",
    "message": "У меня не работает розетка на кухне",
    "channel": "telegram"
  }'
```

#### Step 2: Provide Address
```bash
curl -X POST "http://localhost:8000/api/v1/ai/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_123",
    "message": "ул. Ленина 25, кв. 10",
    "channel": "telegram"
  }'
```

#### Step 3: Send Photo (Optional)
```bash
curl -X POST "http://localhost:8000/api/v1/ai/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_123",
    "message": "Вот фото",
    "channel": "telegram",
    "media_urls": ["https://example.com/outlet.jpg"]
  }'
```

The AI will analyze the photo and generate a quote.

#### Step 4: Confirm Price
```bash
curl -X POST "http://localhost:8000/api/v1/ai/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_123",
    "message": "Да, согласен",
    "channel": "telegram",
    "metadata": {
      "client_name": "Иван Петров",
      "client_phone": "+79001234567"
    }
  }'
```

A job will be created and master matching will begin.

## API Endpoints Reference

### AI Services

- `POST /api/v1/ai/messages` - Process client message
- `POST /api/v1/ai/telegram/message` - Telegram bot integration
- `POST /api/v1/ai/web-form` - Web form submission
- `GET /api/v1/ai/health` - Health check

### Image Analysis

- `POST /api/v1/ai/analyze/image` - Analyze single image
- `POST /api/v1/ai/analyze/images` - Analyze multiple images

### Knowledge Base

- `GET /api/v1/ai/knowledge/solutions` - Get all solutions
- `GET /api/v1/ai/knowledge/solutions/{id}` - Get specific solution

### Conversations

- `GET /api/v1/ai/conversations/active` - Count active conversations
- `GET /api/v1/ai/conversations/{client_id}` - Get conversation status

## Interactive API Documentation

Visit `http://localhost:8000/docs` for:
- ✅ Interactive API testing
- ✅ Request/response schemas
- ✅ Try-it-out functionality
- ✅ Full endpoint documentation

## Run the Demo

```bash
cd backend
python3 demo.py
```

This will simulate a complete conversation flow showing:
1. Client initiates contact
2. AI asks clarifying questions
3. Client provides details and photo
4. AI analyzes and generates quote
5. Client confirms
6. Job is created with full instructions

## Common Issues

### Issue: ModuleNotFoundError

**Solution**: Activate virtual environment and install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database connection error

**Solution**: Check PostgreSQL is running and credentials are correct
```bash
psql -d ai_service -c "SELECT 1"
```

### Issue: Port 8000 already in use

**Solution**: Use different port
```bash
uvicorn main:app --reload --port 8001
```

## Next Steps

1. ✅ Test all API endpoints
2. ✅ Review the API documentation at `/docs`
3. ✅ Read the main README.md for architecture details
4. ✅ Check IMPLEMENTATION_SUMMARY.md for technical details
5. 🔨 Integrate with Telegram Bot API
6. 🔨 Build master mobile application
7. 🔨 Deploy to production

## Development Mode

For development with auto-reload:
```bash
uvicorn main:app --reload --log-level debug
```

## Production Deployment

For production:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use Gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Support

- 📖 Full Documentation: See README.md
- 📋 Implementation Details: See IMPLEMENTATION_SUMMARY.md
- 🔧 API Docs: http://localhost:8000/docs
- 📝 Design Document: .qoder/quests/system-ai-mvp.md

**Happy coding! 🚀**
