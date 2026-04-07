#!/bin/bash
# =====================================================================
# AyahPath Deployment Script for Ubuntu KVM
# Designed for a fresh Ubuntu 22.04/24.04 server
# =====================================================================
set -euo pipefail

APP_DIR="/opt/ayahpath"
APP_USER="ayahpath"
FRONTEND_PORT=5000
API_PORT=5001
VENV_DIR="$APP_DIR/venv"

echo "============================================"
echo "  AyahPath — Ubuntu KVM Deployment Script"
echo "============================================"
echo ""

# ── 1. System dependencies ──────────────────────────────────────────
echo "[1/8] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip nginx git sqlite3 > /dev/null 2>&1
echo "  ✓ System dependencies installed"

# ── 2. Create app user ──────────────────────────────────────────────
echo "[2/8] Setting up application user..."
if ! id "$APP_USER" &>/dev/null; then
    sudo useradd --system --create-home --home-dir "$APP_DIR" --shell /bin/bash "$APP_USER"
    echo "  ✓ Created user: $APP_USER"
else
    echo "  ✓ User $APP_USER already exists"
fi

# ── 3. Copy application files ───────────────────────────────────────
echo "[3/8] Deploying application files..."
sudo mkdir -p "$APP_DIR"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
sudo cp -r "$SCRIPT_DIR"/* "$APP_DIR/"
sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"
echo "  ✓ Application files deployed to $APP_DIR"

# ── 4. Python virtual environment ───────────────────────────────────
echo "[4/8] Setting up Python virtual environment..."
sudo -u "$APP_USER" python3 -m venv "$VENV_DIR"
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --quiet --upgrade pip
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"
echo "  ✓ Python dependencies installed"

# ── 5. Initialize the prayer SQLite database ────────────────────────
echo "[5/8] Initializing prayer database..."
sudo -u "$APP_USER" PRAYER_DB_DIR="$APP_DIR" "$VENV_DIR/bin/python" -c "
from prayer_db import init_db
init_db()
print('  ✓ Prayer database initialized at $APP_DIR/prayer.db')
"

# Verify the schema
echo "  ── Schema verification ──"
sudo -u "$APP_USER" sqlite3 "$APP_DIR/prayer.db" ".tables"
sudo -u "$APP_USER" sqlite3 "$APP_DIR/prayer.db" ".schema prayer_logs"
echo "  ✓ Database schema verified"

# ── 6. Create systemd services ──────────────────────────────────────
echo "[6/8] Creating systemd services..."

# Frontend service
sudo tee /etc/systemd/system/ayahpath-frontend.service > /dev/null <<EOF
[Unit]
Description=AyahPath Frontend (Flask + SQLite Prayer DB)
After=network.target
Wants=ayahpath-api.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="FRONTEND_PORT=$FRONTEND_PORT"
Environment="API_PORT=$API_PORT"
Environment="PRAYER_DB_DIR=$APP_DIR"
ExecStart=$VENV_DIR/bin/gunicorn --bind 127.0.0.1:$FRONTEND_PORT --workers 2 --timeout 120 app:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# API service
sudo tee /etc/systemd/system/ayahpath-api.service > /dev/null <<EOF
[Unit]
Description=AyahPath Backend API
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR/api
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --bind 127.0.0.1:$API_PORT --workers 2 --timeout 120 app:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo "  ✓ Systemd services created"

# ── 7. Configure Nginx reverse proxy ────────────────────────────────
echo "[7/8] Configuring Nginx..."
sudo tee /etc/nginx/sites-available/ayahpath > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Static files — served directly by Nginx for performance
    location /static/ {
        alias /opt/ayahpath/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # Prayer API endpoints (served by frontend Flask app)
    location /api/prayers/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # All other requests → frontend
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/ayahpath /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
echo "  ✓ Nginx configured"

# ── 8. Start services ───────────────────────────────────────────────
echo "[8/8] Starting services..."
sudo systemctl enable ayahpath-api ayahpath-frontend nginx
sudo systemctl restart ayahpath-api
sleep 2
sudo systemctl restart ayahpath-frontend
sudo systemctl restart nginx
echo "  ✓ All services started"

echo ""
echo "============================================"
echo "  ✅ Deployment Complete!"
echo "============================================"
echo ""
echo "  Frontend:  http://$(hostname -I | awk '{print $1}'):80"
echo "  Prayer DB: $APP_DIR/prayer.db"
echo ""
echo "  Useful commands:"
echo "    sudo systemctl status ayahpath-frontend"
echo "    sudo systemctl status ayahpath-api"
echo "    sudo journalctl -u ayahpath-frontend -f"
echo "    sqlite3 $APP_DIR/prayer.db '.tables'"
echo "    sqlite3 $APP_DIR/prayer.db 'SELECT * FROM prayer_logs LIMIT 10;'"
echo ""
