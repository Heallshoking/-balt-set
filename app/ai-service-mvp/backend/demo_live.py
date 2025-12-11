#!/usr/bin/env python3
"""Демонстрация работы системы в реальном времени"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🚀 AI Service Marketplace - LIVE Демонстрация")
print("=" * 70)
print()

# Шаг 1: Регистрация мастера
print("👨‍🔧 ШАГ 1: Регистрация мастера")
print("-" * 70)

master_data = {
    "full_name": "Василий Электриков",
    "phone": "+79991234567",
    "email": "vasily@electric.ru",
    "specializations": ["electrical", "appliances"],
    "experience_years": 7.0,
    "city": "Москва",
    "schedule": {
        "monday": {"available": True, "start_hour": 8, "end_hour": 20},
        "tuesday": {"available": True, "start_hour": 8, "end_hour": 20},
        "wednesday": {"available": True, "start_hour": 8, "end_hour": 20},
        "thursday": {"available": True, "start_hour": 8, "end_hour": 20},
        "friday": {"available": True, "start_hour": 8, "end_hour": 20},
        "saturday": {"available": True, "start_hour": 10, "end_hour": 18},
        "sunday": {"available": False}
    }
}

try:
    response = requests.post(f"{BASE_URL}/api/master/register", json=master_data, timeout=5)
    if response.status_code == 200:
        master = response.json()
        master_id = master["master_id"]
        print(f"✅ Мастер зарегистрирован!")
        print(f"   📋 ID: {master_id}")
        print(f"   👤 Имя: {master['full_name']}")
        print(f"   📱 Телефон: {master['phone']}")
        print(f"   ⭐ Рейтинг: {master.get('rating', 'новый мастер')}")
        print()
        
        # Активация терминала
        print("📱 Активирую терминал мастера...")
        terminal_resp = requests.post(
            f"{BASE_URL}/api/master/{master_id}/activate-terminal",
            json={"terminal_type": "mobile"},
            timeout=5
        )
        if terminal_resp.status_code == 200:
            print("✅ Терминал активирован!")
            print()
            
    else:
        print(f"❌ Ошибка регистрации: {response.status_code}")
        print(response.text[:200])
        exit(1)
        
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    print("💡 Убедитесь что сервер запущен: python3 -m uvicorn main:app")
    exit(1)

# Шаг 2: Заявка от клиента
print("💬 ШАГ 2: Клиент отправляет заявку")
print("-" * 70)

client_message = "Здравствуйте! Не работает розетка в спальне, адрес ул. Пушкина 10, кв. 5"
print(f'Клиент пишет: "{client_message}"')
print()

message_data = {
    "client_id": "demo_client_001",
    "message": client_message,
    "channel": "web",
    "metadata": {
        "client_name": "Мария Ивановна",
        "client_phone": "+79151234567"
    }
}

try:
    ai_resp = requests.post(f"{BASE_URL}/api/ai/process", json=message_data, timeout=10)
    if ai_resp.status_code == 200:
        result = ai_resp.json()
        print("🤖 AI обработал заявку:")
        print(f"   🎯 Намерение: {result['intent']}")
        print(f"   🔧 Категория: {result['extracted_info'].get('problem_category', 'не определена')}")
        print()
        
        if result.get('quote'):
            quote = result['quote']
            print("💰 AI рассчитал стоимость:")
            print(f"   📋 Работа: {quote['solution_name']}")
            print(f"   💵 Стоимость для клиента: {quote['cost_breakdown']['total']:.0f} ₽")
            print(f"   ⏱ Время выполнения: {quote['estimated_duration_hours']} ч")
            print()
            
            print("📤 AI ответил клиенту:")
            print("-" * 70)
            print(result['ai_response'])
            print("-" * 70)
            print()
            
    else:
        print(f"❌ Ошибка AI: {ai_resp.status_code}")
        print(ai_resp.text[:200])
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Шаг 3: Клиент подтверждает
print("✅ ШАГ 3: Клиент подтверждает заказ")
print("-" * 70)

confirm_data = {
    "client_id": "demo_client_001",
    "message": "Да, согласна, оформляйте",
    "channel": "web",
    "metadata": {
        "client_name": "Мария Ивановна",
        "client_phone": "+79151234567"
    }
}

try:
    confirm_resp = requests.post(f"{BASE_URL}/api/ai/process", json=confirm_data, timeout=10)
    if confirm_resp.status_code == 200:
        result = confirm_resp.json()
        
        if result.get('job'):
            job = result['job']
            print("🎉 Заказ создан!")
            print(f"   📋 ID заказа: {job['id'][:20]}...")
            print(f"   💰 Стоимость: {job['client_cost']} ₽")
            print(f"   📍 Адрес: {job.get('location', 'ул. Пушкина 10, кв. 5')}")
            print()
            
            if job.get('master_id'):
                print(f"🎯 Автоматически назначен мастер:")
                print(f"   👤 ID мастера: {job['master_id']}")
                print(f"   💵 Заработок мастера: {job.get('master_earnings', 0)} ₽")
                print(f"   📊 Комиссия платформы: {job.get('platform_commission', 0)} ₽")
                print()
                print("📱 Заказ появился в терминале мастера!")
                print(f"   🔗 Ссылка для мастера: http://localhost:8000/terminal?id={job['master_id']}")
                print()
            else:
                print("⚠️  Мастер не назначен (нет доступных)")
                print()
                
            print("📝 AI ответил клиенту:")
            print("-" * 70)
            print(result['ai_response'])
            print("-" * 70)
            print()
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("=" * 70)
print("✅ Демонстрация завершена!")
print("=" * 70)
print()
print("🌐 Доступные URL:")
print(f"   • API документация: http://localhost:8000/docs")
print(f"   • Health check: http://localhost:8000/health")
print(f"   • Список мастеров: http://localhost:8000/api/master/list")
if 'master_id' in locals():
    print(f"   • Терминал мастера: {BASE_URL}/terminal?id={master_id}")
print()
