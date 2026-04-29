from flask import Flask, request, jsonify, render_template_string
import os
import json
import sys

app = Flask(__name__)

# Railway передает порт через переменную окружения PORT
PORT = int(os.environ.get("PORT", 8080))
KEYS_FILE = "keys.json"

# HTML-шаблон для веб-панели
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>License Server Panel</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        input, button { padding: 8px 12px; margin: 5px; border: 1px solid #ccc; border-radius: 6px; }
        button { background: #0066cc; color: white; cursor: pointer; border: none; }
        button:hover { background: #0052a3; }
        .key-item { font-family: monospace; padding: 8px; border-bottom: 1px solid #eee; }
        .valid { color: green; }
        .invalid { color: gray; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🔑 License Key Manager</h1>
        <p>Сервер работает на порту: <strong>{{ port }}</strong></p>
        
        <form method="POST" action="/add">
            <input type="text" name="key" placeholder="Введите новый ключ" required>
            <button type="submit">➕ Добавить ключ</button>
        </form>
        
        <h2>📋 Существующие ключи</h2>
        <div>
            {% for key_id, key_data in keys.items() %}
            <div class="key-item">
                <code>{{ key_id }}</code> — 
                {% if key_data.active %}
                <span class="valid">✅ Активен</span>
                {% else %}
                <span class="invalid">❌ Использован/Неактивен</span>
                {% endif %}
            </div>
            {% else %}
            <p>Нет активных ключей. Добавьте первый!</p>
            {% endfor %}
        </div>
        <hr>
        <small>API проверки: GET /verify?key=ВАШ_КЛЮЧ</small>
    </div>
</body>
</html>
'''

def load_keys():
    """Загружает ключи из файла"""
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_keys(keys):
    """Сохраняет ключи в файл"""
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

@app.route('/')
def panel():
    """Веб-панель управления ключами"""
    keys = load_keys()
    return render_template_string(HTML_TEMPLATE, keys=keys, port=PORT)

@app.route('/add', methods=['POST'])
def add_key():
    """Добавление нового ключа"""
    key = request.form.get('key', '').strip()
    if not key:
        return 'Ключ не может быть пустым', 400
    
    keys = load_keys()
    if key not in keys:
        keys[key] = {'active': True}
        save_keys(keys)
        return f'<h3>✅ Ключ {key} добавлен!</h3><a href="/">Вернуться</a>'
    else:
        return f'<h3>⚠️ Ключ {key} уже существует</h3><a href="/">Вернуться</a>'

@app.route('/verify')
def verify():
    """API для проверки ключа клиентами"""
    key = request.args.get('key', '').strip()
    if not key:
        return jsonify({'valid': False, 'error': 'Missing key parameter'}), 400
    
    keys = load_keys()
    is_valid = key in keys and keys[key].get('active', False)
    
    # Опционально: пометить ключ как использованный после первой проверки
    # if is_valid and 'used' not in keys[key]:
    #     keys[key]['used'] = True
    #     save_keys(keys)
    
    return jsonify({'valid': is_valid})

@app.route('/keys')
def list_keys():
    """Получить список всех ключей (только для администрирования)"""
    # Можно добавить защиту токеном, если нужно
    return jsonify(load_keys())

if __name__ == '__main__':
    print(f"🚀 Запуск сервера на порту {PORT}")
    app.run(host='0.0.0.0', port=PORT)
