from flask import Flask, request, jsonify, make_response
import os
import json
import hashlib

app = Flask(__name__)

KEYS_FILE = "keys.json"
PORT = int(os.environ.get("PORT", 8080))

# === ПАРОЛЬ ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ ===
# По умолчанию: admin / admin123
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin123")

# === ФУНКЦИИ ДЛЯ КЛЮЧЕЙ ===
def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

# === АУТЕНТИФИКАЦИЯ ===
def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS

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

# === ВЕБ-ПАНЕЛЬ ===
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0e1a;
            font-family: 'Segoe UI', 'Inter', monospace;
            padding: 2rem;
            min-height: 100vh;
            color: #e2e8f0;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            margin-bottom: 2rem;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 1rem;
        }
        .header h1 {
            font-size: 1.75rem;
            font-weight: 500;
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
        .info-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-size: 0.8rem;
            color: #94a3b8;
        }
        .info-box code {
            background: #1e293b;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            color: #60a5fa;
        }
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
            font-size: 0.85rem;
        }
        .btn-primary {
            background: #3b82f6;
            border: none;
            color: white;
        }
        .btn-primary:hover { background: #2563eb; }
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
            font-size: 0.85rem;
            text-transform: uppercase;
            color: #64748b;
            background: #0b1120;
        }
        .key-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #1e293b;
        }
        .key-item:hover { background: #131c2e; }
        .key-code {
            font-family: monospace;
            font-size: 0.85rem;
            background: #1e293b;
            padding: 0.3rem 0.75rem;
            border-radius: 8px;
            word-break: break-all;
        }
        .key-status { display: flex; align-items: center; gap: 1rem; }
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
        .delete-btn:hover { color: #ef4444; background: #7f1d1d30; }
        .empty-state { text-align: center; padding: 3rem; color: #475569; }
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
            <p>key management interface</p>
        </div>
        
        <div class="info-box">
            ℹ️ To change password, set <code>ADMIN_PASS</code> environment variable in Railway dashboard.
        </div>

        <div class="add-section">
            <h2>➕ generate new key</h2>
            <form class="add-form" method="POST" action="/add">
                <input type="text" name="key" placeholder="license-key-xxxx" autocomplete="off">
                <button type="submit" class="btn btn-primary">create</button>
            </form>
        </div>

        <div class="stats">
            <div class="stat-card"><span>total keys</span><span id="totalCount">0</span></div>
            <div class="stat-card"><span>active</span><span id="activeCount">0</span></div>
        </div>

        <div class="keys-section">
            <div class="keys-header">licensed keys</div>
            <div id="keysList"><div class="empty-state">⸻ no keys loaded ⸻</div></div>
        </div>
        <div class="footer">api endpoint → GET /verify?key=&lt;key&gt;</div>
    </div>
    <script>
        function loadKeys() {
            fetch('/api/keys').then(r=>r.json()).then(keys => {
                const container = document.getElementById('keysList');
                const entries = Object.entries(keys);
                const activeCount = entries.filter(([_, d]) => d.active).length;
                document.getElementById('totalCount').innerText = entries.length;
                document.getElementById('activeCount').innerText = activeCount;
                if (entries.length === 0) {
                    container.innerHTML = '<div class="empty-state">⸻ no keys loaded ⸻</div>';
                    return;
                }
                container.innerHTML = entries.map(([key, data]) => `
                    <div class="key-item">
                        <code class="key-code">${escapeHtml(key)}</code>
                        <div class="key-status">
                            <span class="badge ${data.active ? 'badge-active' : 'badge-inactive'}">${data.active ? '● active' : '○ used'}</span>
                            <button class="delete-btn" onclick="deleteKey('${escapeHtml(key)}')">✕</button>
                        </div>
                    </div>
                `).join('');
            });
        }
        function escapeHtml(str) { return str.replace(/[&<>]/g, function(m) { return m === '&' ? '&amp;' : m === '<' ? '&lt;' : '&gt;'; }); }
        function deleteKey(key) {
            if (confirm(`revoke key: ${key}?`)) {
                fetch('/delete', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: 'key=' + encodeURIComponent(key) }).then(() => loadKeys());
            }
        }
        loadKeys();
    </script>
</body>
</html>'''
    return html

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

@app.route('/verify')
def verify():
    key = request.args.get('key', '').strip()
    keys = load_keys()
    is_valid = key in keys and keys[key].get('active', False)
    return jsonify({'valid': is_valid})

@app.route('/addnew')
def fake_addnew():
    return '<h1>404</h1><p>Page not found.</p>', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
