"""
Демо-данные для быстрого тестирования AI Service Marketplace MVP

Запуск:
    cd backend
    python3 demo.py

Это создаст тестовых мастеров и заказы для проверки работы системы.
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/v1"

# Цвета для красивого вывода
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")


def create_demo_masters():
    """Создать демонстрационных мастеров"""
    print("\n" + "="*60)
    print_info("Создание тестовых мастеров...")
    print("="*60)
    
    masters = [
        {
            "full_name": "Иванов Иван Иванович",
            "phone": "+79001234567",
            "email": "ivanov@example.com",
            "specializations": ["electrical", "appliances"],
            "experience_years": 5.0,
            "city": "Москва",
            "preferred_channel": "telegram",
            "telegram_chat_id": "123456789"
        },
        {
            "full_name": "Петров Пётр Петрович",
            "phone": "+79007654321",
            "email": "petrov@example.com",
            "specializations": ["plumbing"],
            "experience_years": 3.0,
            "city": "Москва",
            "preferred_channel": "telegram"
        },
        {
            "full_name": "Сидоров Сергей Сергеевич",
            "phone": "+79009876543",
            "email": "sidorov@example.com",
            "specializations": ["electrical", "renovation"],
            "experience_years": 7.0,
            "city": "Москва",
            "preferred_channel": "phone"
        }
    ]
    
    created_masters = []
    
    for master_data in masters:
        try:
            response = requests.post(f"{API_URL}/masters/register", json=master_data)
            if response.status_code == 200:
                result = response.json()
                master_id = result["master_id"]
                created_masters.append({
                    "id": master_id,
                    "name": master_data["full_name"],
                    "specs": master_data["specializations"]
                })
                print_success(f"Создан мастер: {master_data['full_name']} (ID: {master_id[:8]}...)")
                
                # Установить расписание
                schedule = {
                    "monday": {"available": True, "start_hour": 8, "end_hour": 20},
                    "tuesday": {"available": True, "start_hour": 8, "end_hour": 20},
                    "wednesday": {"available": True, "start_hour": 8, "end_hour": 20},
                    "thursday": {"available": True, "start_hour": 8, "end_hour": 20},
                    "friday": {"available": True, "start_hour": 8, "end_hour": 20},
                    "saturday": {"available": True, "start_hour": 9, "end_hour": 18},
                    "sunday": {"available": False}
                }
                
                schedule_response = requests.put(
                    f"{API_URL}/masters/{master_id}/schedule",
                    json={"schedule": schedule}
                )
                
                if schedule_response.status_code == 200:
                    print_success(f"  └─ Расписание установлено (Пн-Пт 8-20, Сб 9-18)")
                
                # Активировать терминал
                terminal_response = requests.post(
                    f"{API_URL}/masters/{master_id}/activate-terminal",
                    json={"terminal_type": "mobile"}
                )
                
                if terminal_response.status_code == 200:
                    print_success(f"  └─ Мобильный терминал активирован")
                    print_info(f"  └─ Ссылка: http://localhost:3000/master/terminal.html?id={master_id}")
            else:
                print_warning(f"Ошибка создания мастера: {master_data['full_name']}")
                
        except Exception as e:
            print_warning(f"Ошибка: {e}")
    
    return created_masters


def create_demo_client_request():
    """Создать демонстрационную заявку от клиента"""
    print("\n" + "="*60)
    print_info("Создание тестовой заявки от клиента...")
    print("="*60)
    
    client_request = {
        "name": "Иван Клиентов",
        "phone": "+79005551234",
        "email": "client@example.com",
        "category": "electrical",
        "problem_description": "Не работает розетка на кухне, при включении чайника ничего не происходит",
        "address": "ул. Ленина 25, кв. 10",
        "preferred_time": "Как можно скорее"
    }
    
    try:
        response = requests.post(f"{API_URL}/ai/web-form", json=client_request)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Заявка создана успешно!")
            
            if result.get("job"):
                job = result["job"]
                print_info(f"  └─ ID заказа: {job['id'][:8]}...")
                print_info(f"  └─ Категория: {job['category']}")
                print_info(f"  └─ Стоимость: {job['client_cost']} руб.")
                
                if job.get("master_id"):
                    print_success(f"  └─ Автоматически назначен мастер: {job['master_id'][:8]}...")
                    print_info(f"  └─ Статус: {job['status']}")
                else:
                    print_warning("  └─ Мастер не найден (нет доступных мастеров)")
            
            if result.get("ai_response"):
                print("\n" + "─"*60)
                print_info("Ответ AI системы клиенту:")
                print(f"  {result['ai_response']}")
                print("─"*60)
                
        else:
            print_warning(f"Ошибка создания заявки: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_warning(f"Ошибка: {e}")


def show_summary():
    """Показать итоговую информацию"""
    print("\n" + "="*60)
    print_success("ДЕМО-ДАННЫЕ СОЗДАНЫ!")
    print("="*60)
    print()
    print("📱 Доступные страницы:")
    print(f"   • API документация: {Colors.BLUE}http://localhost:8000/docs{Colors.END}")
    print(f"   • Форма для клиентов: {Colors.BLUE}http://localhost:3000/index.html{Colors.END}")
    print(f"   • Терминал мастера: {Colors.BLUE}http://localhost:3000/master/terminal.html?id=<master_id>{Colors.END}")
    print()
    print("🔧 Что делать дальше:")
    print("   1. Откройте терминал мастера (ссылка выше)")
    print("   2. Создайте новую заявку через форму клиента")
    print("   3. Заявка автоматически появится у мастера в терминале")
    print("   4. Мастер примет заказ и обработает оплату")
    print()


if __name__ == "__main__":
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  AI Service Marketplace - Создание демо-данных{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    try:
        # Проверка доступности API
        print_info("Проверка подключения к API...")
        response = requests.get(f"{API_URL.replace('/api/v1', '')}/health", timeout=3)
        if response.status_code == 200:
            print_success("API доступен")
        else:
            print_warning("API вернул неожиданный код")
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} Не удалось подключиться к API")
        print(f"  Убедитесь, что сервер запущен: {Colors.YELLOW}./run.sh{Colors.END}")
        exit(1)
    
    # Создать мастеров
    masters = create_demo_masters()
    
    # Создать заявку от клиента
    create_demo_client_request()
    
    # Показать итоги
    show_summary()
