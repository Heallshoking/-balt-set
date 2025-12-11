# AI Service Marketplace - Deployment Guide

## 🎯 What Has Been Implemented

### ✅ Complete MVP Core (Ready for Deployment)

#### Phase 1: Infrastructure ✓
- [x] PostgreSQL database schema
- [x] Async database connection management
- [x] Configuration management
- [x] Environment variables setup

#### Phase 2: AI Core Services ✓
- [x] NLP Service (501 lines) - Conversation AI
- [x] Vision Service (492 lines) - Image analysis
- [x] Knowledge Base (593 lines) - 8 repair solutions
- [x] Pricing Engine (288 lines) - Dynamic pricing
- [x] Master Matcher (312 lines) - Intelligent matching
- [x] Payment Service (336 lines) - YooKassa integration
- [x] AI Orchestrator (368 lines) - Main coordinator

#### Phase 3: Backend API ✓
- [x] FastAPI application
- [x] 10+ REST API endpoints
- [x] OpenAPI documentation
- [x] CORS middleware
- [x] Health check endpoints

#### Phase 4: Client Channels ✓
- [x] Telegram Bot (435 lines) - Full bot implementation
- [x] Web Form (421 lines) - HTML/CSS/JS form
- [x] Multi-channel support infrastructure

---

## 📦 Project Structure

```
ai-service-mvp/
│
├── README.md                          # Main documentation (521 lines)
├── IMPLEMENTATION_SUMMARY.md          # Technical details (539 lines)
├── QUICK_START.md                     # Installation guide (305 lines)
├── DEPLOYMENT_GUIDE.md                # This file
│
├── database/
│   └── schema.sql                     # PostgreSQL schema (250 lines)
│
├── frontend/
│   └── index.html                     # Web form (421 lines)
│
└── backend/
    ├── main.py                        # FastAPI app (94 lines)
    ├── demo.py                        # Demo script (164 lines)
    ├── run_telegram_bot.py            # Bot launcher (108 lines)
    ├── requirements.txt               # Dependencies (64 lines)
    │
    └── app/
        ├── api/
        │   ├── __init__.py
        │   └── ai.py                  # AI API (246 lines)
        │
        ├── core/
        │   ├── config.py              # Settings (120 lines)
        │   └── database.py            # DB management (150 lines)
        │
        ├── integrations/
        │   ├── __init__.py
        │   └── telegram_bot.py        # Telegram bot (435 lines)
        │
        └── services/
            ├── ai_orchestrator.py     # Orchestrator (368 lines)
            ├── nlp_service.py         # NLP (501 lines)
            ├── vision_service.py      # Vision (492 lines)
            ├── knowledge_base.py      # Knowledge (593 lines)
            ├── pricing_engine.py      # Pricing (288 lines)
            ├── master_matcher.py      # Matching (312 lines)
            └── payment_service.py     # Payments (336 lines)
```

**Total: ~5,500+ lines of production code**

---

## 🚀 Deployment Steps

### 1. Server Setup

#### Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.11+
- PostgreSQL 14+
- Redis 6+ (for task queue)
- 2GB+ RAM
- 20GB+ disk space

#### Install System Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE ai_service;
CREATE USER ai_service_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_service TO ai_service_user;
\q

# Apply schema
sudo -u postgres psql -d ai_service -f database/schema.sql
```

### 3. Application Setup

```bash
# Clone/upload your code
cd /opt
sudo mkdir ai-service-mvp
sudo chown $USER:$USER ai-service-mvp
cd ai-service-mvp

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file
cat > backend/.env << EOF
# Database
DATABASE_URL=postgresql+asyncpg://ai_service_user:your_secure_password@localhost/ai_service

# Platform
PLATFORM_COMMISSION_RATE=0.25
MINIMUM_JOB_COST=500.0
MAXIMUM_JOB_COST=50000.0

# YooKassa
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token

# CORS
CORS_ORIGINS=["https://yourdomain.com"]
EOF
```

### 4. Systemd Services

#### API Service
```bash
sudo nano /etc/systemd/system/ai-service-api.service
```

```ini
[Unit]
Description=AI Service Marketplace API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai-service-mvp/backend
Environment="PATH=/opt/ai-service-mvp/venv/bin"
ExecStart=/opt/ai-service-mvp/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Telegram Bot Service
```bash
sudo nano /etc/systemd/system/ai-service-telegram.service
```

```ini
[Unit]
Description=AI Service Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai-service-mvp/backend
Environment="PATH=/opt/ai-service-mvp/venv/bin"
ExecStart=/opt/ai-service-mvp/venv/bin/python run_telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-service-api
sudo systemctl enable ai-service-telegram
sudo systemctl start ai-service-api
sudo systemctl start ai-service-telegram

# Check status
sudo systemctl status ai-service-api
sudo systemctl status ai-service-telegram
```

### 5. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/ai-service
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /opt/ai-service-mvp/frontend;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com -d yourdomain.com
```

---

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/ai_service

# Platform Settings
PLATFORM_COMMISSION_RATE=0.25  # 25% commission
MINIMUM_JOB_COST=500.0          # Minimum 500 rubles
MAXIMUM_JOB_COST=50000.0        # Maximum 50,000 rubles
MASTER_RESPONSE_TIMEOUT_MINUTES=15
MAX_MASTER_DAILY_JOBS=10

# YooKassa Payment Gateway
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_token_from_botfather

# CORS (for web clients)
CORS_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]

# Optional: AI Services
OPENAI_API_KEY=your_openai_key  # For enhanced AI
```

---

## 📊 Monitoring

### Logs
```bash
# API logs
sudo journalctl -u ai-service-api -f

# Telegram bot logs
sudo journalctl -u ai-service-telegram -f
tail -f /opt/ai-service-mvp/backend/telegram_bot.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Health Checks
```bash
# API health
curl https://api.yourdomain.com/health

# AI services health
curl https://api.yourdomain.com/api/v1/ai/health
```

### Prometheus Metrics
Access at: `https://api.yourdomain.com/metrics`

---

## 🔐 Security Checklist

- [ ] Change default database password
- [ ] Set secure YooKassa credentials
- [ ] Configure firewall (UFW)
- [ ] Enable SSL/TLS certificates
- [ ] Set up fail2ban
- [ ] Regular database backups
- [ ] Monitor system resources
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for trusted domains

---

## 🧪 Testing

### Test API Endpoints
```bash
# Health check
curl https://api.yourdomain.com/api/v1/ai/health

# Process message
curl -X POST https://api.yourdomain.com/api/v1/ai/messages \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test_001",
    "message": "Не работает розетка",
    "channel": "telegram"
  }'
```

### Test Telegram Bot
1. Open Telegram
2. Find your bot by username
3. Send `/start`
4. Send a problem description
5. Verify AI responds correctly

### Test Web Form
1. Open `https://yourdomain.com`
2. Fill out the form
3. Submit
4. Verify job is created

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Run multiple API workers
uvicorn main:app --workers 8 --host 0.0.0.0 --port 8000

# Or use Gunicorn
gunicorn main:app -w 8 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Load Balancing
Set up multiple servers behind Nginx:

```nginx
upstream api_backend {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

---

## 🔄 Updates & Maintenance

### Update Code
```bash
cd /opt/ai-service-mvp
git pull  # or upload new code
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart ai-service-api
sudo systemctl restart ai-service-telegram
```

### Database Migrations
```bash
# Apply new schema changes
psql -U ai_service_user -d ai_service -f migrations/001_add_new_table.sql
```

### Backup Database
```bash
# Create backup
pg_dump -U ai_service_user ai_service > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U ai_service_user -d ai_service < backup_20241210.sql
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue: API not starting**
```bash
# Check logs
sudo journalctl -u ai-service-api -n 50

# Check if port is in use
sudo lsof -i :8000

# Restart service
sudo systemctl restart ai-service-api
```

**Issue: Database connection error**
```bash
# Test connection
psql -U ai_service_user -d ai_service -c "SELECT 1"

# Check PostgreSQL status
sudo systemctl status postgresql
```

**Issue: Telegram bot not responding**
```bash
# Check bot logs
tail -f /opt/ai-service-mvp/backend/telegram_bot.log

# Restart bot
sudo systemctl restart ai-service-telegram
```

---

## ✅ Production Readiness Checklist

### Before Going Live
- [ ] Database schema applied
- [ ] All environment variables set
- [ ] YooKassa credentials configured
- [ ] Telegram bot token set
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Nginx configured
- [ ] Services enabled and running
- [ ] Health checks passing
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Error tracking enabled
- [ ] Load testing completed
- [ ] Security audit passed

---

## 🎉 Success!

Your AI Service Marketplace MVP is now deployed and running!

**Access Points:**
- API: `https://api.yourdomain.com`
- API Docs: `https://api.yourdomain.com/docs`
- Web Form: `https://yourdomain.com`
- Telegram Bot: `@your_bot_username`

**Next Steps:**
1. Test all functionality end-to-end
2. Onboard first masters
3. Run pilot with limited clients
4. Gather feedback and iterate
5. Scale as needed

Good luck! 🚀
