from flask import Flask, request, jsonify, make_response
import os
import json

app = Flask(__name__)

KEYS_FILE = "keys.json"
CONFIG_FILE = "config.json"
PORT = int(os.environ.get("PORT", 8080))

# === ЗАГРУЗКА/СОХРАНЕНИЕ КОНФИГА ===
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"admin_user": "kiberpunk", "admin_pass": "Xk9#mP2$vL5@qR7!wN3"}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# === АУТЕНТИФИКАЦИЯ ===
def check_auth(username, password):
    config = load_config()
    return username == config.get("admin_user") and password == config.get("admin_pass")

def authenticate():
    return make_response(
        '<h1 style="background:#0a0e1a;color:#e2e8f0;padding:2rem;font-family:monospace;">🔐 Access Denied</h1>', 401,
        {'WWW-Authenticate': 'Basic realm="License Admin Panel"'}
    )

def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# === ФУНКЦИИ ДЛЯ КЛЮЧЕЙ ===
def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

# === ВЕБ-ПАНЕЛЬ (ЗАЩИЩЕНА) ===
@app.route('/')
@requires_auth
def panel():
    keys = load_keys()
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Server | Admin Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0e1a;
            font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, monospace;
            padding: 2rem;
            min-height: 100vh;
            color: #e2e8f0;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        .header {
            margin-bottom: 2rem;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 1rem;
        }

        .header h1 {
            font-size: 1.75rem;
            font-weight: 500;
            letter-spacing: -0.3px;
            background: linear-gradient(135deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .header p {
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 0.5rem;
            font-family: monospace;
        }

        /* Password Change Section */
        .password-section {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .password-section h2 {
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 1rem;
            color: #fbbf24;
        }

        .password-form {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            align-items: flex-end;
        }

        .password-field {
            flex: 1;
            min-width: 180px;
        }

        .password-field label {
            display: block;
            font-size: 0.7rem;
            color: #64748b;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .password-field input {
            width: 100%;
            background: #1e293b;
            border: 1px solid #334155;
            padding: 0.6rem 0.8rem;
            border-radius: 10px;
            color: #f1f5f9;
            font-family: monospace;
            font-size: 0.85rem;
        }

        .password-field input:focus {
            outline: none;
            border-color: #fbbf24;
        }

        /* Add Key Section */
        .add-section {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .add-section h2 {
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 1rem;
            color: #cbd5e1;
        }

        .add-form {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }

        .add-form input {
            flex: 1;
            min-width: 200px;
            background: #1e293b;
            border: 1px solid #334155;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            color: #f1f5f9;
            font-family: monospace;
            font-size: 0.9rem;
        }

        .add-form input:focus {
            outline: none;
            border-color: #60a5fa;
        }

        .btn {
            background: #1e293b;
            border: 1px solid #334155;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            color: #e2e8f0;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.85rem;
        }

        .btn-primary {
            background: #3b82f6;
            border: none;
            color: white;
        }

        .btn-primary:hover {
            background: #2563eb;
        }

        .btn-warning {
            background: #d97706;
            border: none;
            color: white;
        }

        .btn-warning:hover {
            background: #b45309;
        }

        .stats {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .stat-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 0.75rem 1.25rem;
        }

        .stat-card span:first-child {
            color: #64748b;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-card span:last-child {
            font-size: 1.5rem;
            font-weight: 600;
            margin-left: 0.75rem;
            color: #60a5fa;
        }

        .keys-section {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 16px;
            overflow: hidden;
        }

        .keys-header {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #1e293b;
            font-weight: 500;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
            background: #0b1120;
        }

        .key-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #1e293b;
            transition: background 0.15s;
        }

        .key-item:hover {
            background: #131c2e;
        }

        .key-code {
            font-family: monospace;
            font-size: 0.85rem;
            background: #1e293b;
            padding: 0.3rem 0.75rem;
            border-radius: 8px;
            word-break: break-all;
        }

        .key-status {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 500;
        }

        .badge-active {
            background: #15803d20;
            color: #4ade80;
            border: 1px solid #15803d;
        }

        .badge-inactive {
            background: #7f1d1d20;
            color: #f87171;
            border: 1px solid #7f1d1d;
        }

        .delete-btn {
            background: none;
            border: none;
            color: #64748b;
            cursor: pointer;
            font-size: 1.2rem;
            padding: 0.25rem 0.5rem;
            border-radius: 8px;
        }

        .delete-btn:hover {
            color: #ef4444;
            background: #7f1d1d30;
        }

        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #475569;
        }

        .success-msg, .error-msg {
            padding: 0.5rem 1rem;
            border-radius: 10px;
            font-size: 0.8rem;
            margin-bottom: 1rem;
        }

        .success-msg {
            background: #15803d20;
            border: 1px solid #15803d;
            color: #4ade80;
        }

        .error-msg {
            background: #7f1d1d20;
            border: 1px solid #7f1d1d;
            color: #f87171;
        }

        .footer {
            margin-top: 2rem;
            text-align: center;
            font-size: 0.7rem;
            color: #334155;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✦ licensectl</h1>
            <p>authentication required · key management interface</p>
        </div>

        <div id="passwordMsg"></div>
        <div class="password-section">
            <h2>🔐 change admin password</h2>
            <form class="password-form" method="POST" action="/change_password" id="passwordForm">
                <div class="password-field">
                    <label>current password</label>
                    <input type="password" name="current_pass" required>
                </div>
                <div class="password-field">
                    <label>new password</label>
                    <input type="password" name="new_pass" required>
                </div>
                <div class="password-field">
                    <label>confirm new</label>
                    <input type="password" name="confirm_pass" required>
                </div>
                <button type="submit" class="btn btn-warning">update password</button>
            </form>
        </div>

        <div class="add-section">
            <h2>➕ generate new key</h2>
            <form class="add-form" method="POST" action="/add">
                <input type="text" name="key" placeholder="license-key-xxxx" autocomplete="off">
                <button type="submit" class="btn btn-primary">create</button>
            </form>
        </div>

        <div class="stats">
            <div class="stat-card">
                <span>total keys</span>
                <span id="totalCount">0</span>
            </div>
            <div class="stat-card">
                <span>active</span>
                <span id="activeCount">0</span>
            </div>
        </div>

        <div class="keys-section">
            <div class="keys-header">licensed keys</div>
            <div id="keysList">
                <div class="empty-state">⸻ no keys loaded ⸻</div>
            </div>
        </div>
        <div class="footer">
            api endpoint → GET /verify?key=&lt;key&gt;
        </div>
    </div>

    <script>
        function loadKeys() {
            fetch('/api/keys')
                .then(r => r.json())
                .then(keys => {
                    const container = document.getElementById('keysList');
                    const totalSpan = document.getElementById('totalCount');
                    const activeSpan = document.getElementById('activeCount');
                    
                    const entries = Object.entries(keys);
                    const activeCount = entries.filter(([_, d]) => d.active).length;
                    
                    totalSpan.innerText = entries.length;
                    activeSpan.innerText = activeCount;
                    
                    if (entries.length === 0) {
                        container.innerHTML = '<div class="empty-state">⸻ no keys loaded ⸻</div>';
                        return;
                    }
                    
                    container.innerHTML = entries.map(([key, data]) => `
                        <div class="key-item">
                            <code class="key-code">${escapeHtml(key)}</code>
                            <div class="key-status">
                                <span class="badge ${data.active ? 'badge-active' : 'badge-inactive'}">
                                    ${data.active ? '● active' : '○ used/disabled'}
                                </span>
                                <button class="delete-btn" onclick="deleteKey('${escapeHtml(key)}')" title="revoke key">✕</button>
                            </div>
                        </div>
                    `).join('');
                });
        }
        
        function escapeHtml(str) {
            return str.replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
        }
        
        function deleteKey(key) {
            if (confirm(`revoke key: ${key}?`)) {
                fetch('/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: 'key=' + encodeURIComponent(key)
                }).then(() => loadKeys());
            }
        }

        // Обработка смены пароля через fetch
        document.getElementById('passwordForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const msgDiv = document.getElementById('passwordMsg');
            
            try {
                const resp = await fetch('/change_password', {
                    method: 'POST',
                    body: formData
                });
                const text = await resp.text();
                if (resp.ok) {
                    msgDiv.innerHTML = '<div class="success-msg">✓ ' + text + '</div>';
                    e.target.reset();
                    setTimeout(() => { msgDiv.innerHTML = ''; }, 3000);
                } else {
                    msgDiv.innerHTML = '<div class="error-msg">✗ ' + text + '</div>';
                }
            } catch (err) {
                msgDiv.innerHTML = '<div class="error-msg">✗ connection error</div>';
            }
        });
        
        loadKeys();
    </script>
</body>
</html>'''
    return html

# === СМЕНА ПАРОЛЯ ===
@app.route('/change_password', methods=['POST'])
@requires_auth
def change_password():
    current = request.form.get('current_pass', '').strip()
    new_pass = request.form.get('new_pass', '').strip()
    confirm = request.form.get('confirm_pass', '').strip()
    
    config = load_config()
    
    if current != config.get("admin_pass"):
        return "Current password is incorrect", 400
    
    if len(new_pass) < 6:
        return "New password must be at least 6 characters", 400
    
    if new_pass != confirm:
        return "New passwords do not match", 400
    
    if new_pass == current:
        return "New password must be different from current", 400
    
    config["admin_pass"] = new_pass
    save_config(config)
    
    return "Password changed successfully! Please re-login with new password", 200

# === API ДЛЯ AJAX ===
@app.route('/api/keys')
@requires_auth
def api_keys():
    return jsonify(load_keys())

@app.route('/add', methods=['POST'])
@requires_auth
def add_key():
    key = request.form.get('key', '').strip()
    if not key:
        return 'Key cannot be empty', 400
    keys = load_keys()
    if key not in keys:
        keys[key] = {'active': True}
        save_keys(keys)
    return '<script>window.location.href="/"</script>'

@app.route('/delete', methods=['POST'])
@requires_auth
def delete_key():
    key = request.form.get('key', '').strip()
    keys = load_keys()
    if key in keys:
        del keys[key]
        save_keys(keys)
    return '', 200

# === ПУБЛИЧНЫЙ API ===
@app.route('/verify')
def verify():
    key = request.args.get('key', '').strip()
    keys = load_keys()
    is_valid = key in keys and keys[key].get('active', False)
    return jsonify({'valid': is_valid})

# === МАСКИРОВКА ===
@app.route('/addnew')
def fake_addnew():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>404</title><style>body{background:#0a0e1a;color:#aaa;font-family:monospace;padding:2rem;}</style></head>
    <body>
        <h1>404</h1>
        <p>Page not found.</p>
    </body>
    </html>
    ''', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
