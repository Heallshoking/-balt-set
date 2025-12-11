#!/usr/bin/env python3
"""
Тестирование работы AI Service Marketplace
"""

import sys
sys.path.insert(0, '.')

print("="*60)
print("🚀 AI Service Marketplace - Демонстрация работы")
print("="*60)
print()

# Шаг 1: Проверка импортов
print("📦 Шаг 1: Проверка модулей...")
try:
    from main import app
    print("  ✅ FastAPI приложение загружено")
    
    from app.api import master, terminal, ai
    print("  ✅ API endpoints загружены")
    
    from app.services.ai_orchestrator import AIOrchestrator
    print("  ✅ AI Orchestrator готов")
    
    from app.services.nlp_service import NLPService
    from app.services.vision_service import VisionService
    from app.services.knowledge_base import KnowledgeBase
    from app.services.pricing_engine import PricingEngine
    print("  ✅ Все AI сервисы загружены")
    
except ImportError as e:
    print(f"  ❌ Ошибка импорта: {e}")
    sys.exit(1)

print()

# Шаг 2: Создание тестового мастера
print("👨‍🔧 Шаг 2: Создание тестового мастера...")
from app.api.master import masters_db

master_id = "test-master-001"
masters_db[master_id] = {
    "id": master_id,
    "full_name": "Тестовый Электрик Иванович",
    "phone": "+79001234567",
    "email": "test@example.com",
    "specializations": ["electrical", "appliances"],
    "experience_years": 5.0,
    "city": "Москва",
    "status": "active",
    "schedule": {
        "monday": {"available": True, "start_hour": 8, "end_hour": 20},
        "tuesday": {"available": True, "start_hour": 8, "end_hour": 20},
        "wednesday": {"available": True, "start_hour": 8, "end_hour": 20},
        "thursday": {"available": True, "start_hour": 8, "end_hour": 20},
        "friday": {"available": True, "start_hour": 8, "end_hour": 20},
        "saturday": {"available": True, "start_hour": 9, "end_hour": 18},
        "sunday": {"available": False}
    },
    "terminal_type": "mobile",
    "terminal_activated": "2024-01-01T10:00:00",
    "rating": 4.8,
    "completed_jobs": 127,
    "total_jobs": 135
}

print(f"  ✅ Мастер создан: {masters_db[master_id]['full_name']}")
print(f"  📱 ID: {master_id}")
print(f"  ⭐ Рейтинг: {masters_db[master_id]['rating']}")
print(f"  📊 Выполнено заказов: {masters_db[master_id]['completed_jobs']}")
print()

# Шаг 3: Тестирование AI обработки заявки
print("🤖 Шаг 3: Обработка заявки от клиента через AI...")

orchestrator = AIOrchestrator()
client_id = "test_client_001"

# Симуляция сообщения от клиента
test_message = "Здравствуйте! Не работает розетка на кухне, при включении чайника ничего не происходит. Адрес: ул. Ленина 25, кв. 10"

print(f"  💬 Сообщение клиента:")
print(f"     '{test_message}'")
print()

import asyncio

async def test_processing():
    result = await orchestrator.process_client_message(
        client_id=client_id,
        message=test_message,
        channel="web",
        metadata={"client_name": "Иван Клиентов", "client_phone": "+79009876543"}
    )
    
    print("  🧠 AI обработал сообщение:")
    print(f"     Намерение: {result['intent']}")
    print(f"     Категория: {result['extracted_info'].get('problem_category', 'не определена')}")
    print(f"     Срочность: {result['extracted_info'].get('urgency', 'normal')}")
    print()
    
    if result.get('quote'):
        quote = result['quote']
        print("  💰 Расчёт стоимости:")
        print(f"     Проблема: {quote['problem_description']}")
        print(f"     Стоимость для клиента: {quote['cost_breakdown']['total']:.0f} ₽")
        print(f"     Заработок мастера: ~{quote['cost_breakdown']['total'] * 0.73:.0f} ₽")
        print(f"     Время выполнения: {quote['estimated_duration_hours']} ч")
        print()
    
    # Подтверждение заказа
    print("  ✅ Клиент подтверждает заказ...")
    confirm_result = await orchestrator.process_client_message(
        client_id=client_id,
        message="Да, согласен, оформляйте",
        channel="web",
        metadata={"client_name": "Иван Клиентов", "client_phone": "+79009876543"}
    )
    
    if confirm_result.get('job'):
        job = confirm_result['job']
        print()
        print("  📋 Заказ создан:")
        print(f"     ID: {job['id'][:16]}...")
        print(f"     Категория: {job['category']}")
        print(f"     Адрес: {job.get('location', 'Не указан')}")
        print(f"     Стоимость: {job['client_cost']} ₽")
        print(f"     Заработок мастера: {job.get('master_earnings', 0)} ₽")
        print()
        
        if job.get('master_id'):
            print(f"  🎯 Автоматически назначен мастер: {job['master_id']}")
            print(f"  📱 Статус: {job['status']}")
            print()
            
            if job.get('instructions'):
                print("  📝 Инструкция для мастера создана:")
                instructions = job['instructions']
                print(f"     Название работы: {instructions.get('job_title', 'Не указано')}")
                if instructions.get('required_tools'):
                    print(f"     Инструменты: {', '.join(instructions['required_tools'][:3])}")
                print()
        else:
            print("  ⚠️  Мастер не назначен (нет доступных мастеров)")
            print()
    
    return confirm_result.get('job')

# Запуск асинхронной функции
job = asyncio.run(test_processing())

# Шаг 4: Проверка терминала мастера
if job and job.get('master_id'):
    print("="*60)
    print("📱 Шаг 4: Терминал мастера")
    print("="*60)
    print()
    
    from app.api.terminal import jobs_db
    
    if job['id'] in jobs_db:
        terminal_job = jobs_db[job['id']]
        print(f"  ✅ Заказ появился в терминале мастера")
        print(f"  📋 Мастер видит:")
        print(f"     Клиент: {terminal_job.get('client_name', 'Не указан')}")
        print(f"     Телефон: {terminal_job.get('client_phone', 'Не указан')}")
        print(f"     Проблема: {terminal_job.get('problem_description', '')[:50]}...")
        print(f"     Адрес: {terminal_job.get('location', terminal_job.get('address', 'Не указан'))}")
        print(f"     Заработок: {terminal_job.get('master_earnings', 0)} ₽")
        print()

print("="*60)
print("✅ Демонстрация завершена успешно!")
print("="*60)
print()
print("🔗 Ссылки для тестирования:")
print(f"   • API документация: http://localhost:8000/docs")
print(f"   • Форма клиента: file://./frontend/index.html")
print(f"   • Терминал мастера: file://./frontend/master/terminal.html?id={master_id}")
print()
print("💡 Запустите сервер: python3 -m uvicorn main:app --reload")
print("   Затем откройте ссылки выше в браузере")
print()
