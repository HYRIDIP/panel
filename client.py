import requests
import sys

# Замените на ваш реальный URL от Railway
SERVER_URL = "https://ваш-проект.up.railway.app"  

def check_license():
    key = input("🔑 Введите лицензионный ключ: ").strip()
    try:
        response = requests.get(f"{SERVER_URL}/verify", params={'key': key}, timeout=5)
        if response.status_code == 200 and response.json().get('valid'):
            print("✅ Доступ разрешен")
            return True
        else:
            print("❌ Неверный ключ")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу лицензий")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if not check_license():
    sys.exit(1)

# --- Ваш основной код программы идет здесь ---
print("Программа запущена!")
