#!/bin/bash
#
# VPS Deployment Script for SmartGardenHub
# Database: /var/www/saroyarsir/smartgardenhub.db
# Port: 8001

set -e  # Exit on error

echo "======================================================================"
echo "  SMARTGARDENHUB VPS DEPLOYMENT"
echo "======================================================================"
echo ""

# Configuration
APP_DIR="/var/www/saroyarsir"
DB_PATH="/var/www/saroyarsir/smartgardenhub.db"
BACKUP_DIR="/var/www/saroyarsir/backups"
PORT=8001
APP_NAME="smartgardenhub"

echo "📋 Configuration:"
echo "   App Directory: $APP_DIR"
echo "   Database: $DB_PATH"
echo "   Backup Directory: $BACKUP_DIR"
echo "   Port: $PORT"
echo ""

# Step 1: Create necessary directories
echo "📁 Step 1: Creating directories..."
mkdir -p "$APP_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/instance"
mkdir -p "$APP_DIR/static/uploads"
mkdir -p "$APP_DIR/flask_session"
echo "✅ Directories created"

# Step 2: Set proper permissions
echo "🔒 Step 2: Setting permissions..."
chown -R $USER:$USER "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod -R 775 "$BACKUP_DIR"
chmod -R 775 "$APP_DIR/instance"
chmod -R 775 "$APP_DIR/logs"
chmod -R 775 "$APP_DIR/flask_session"
echo "✅ Permissions set"

# Step 3: Install Python dependencies
echo "📦 Step 3: Installing Python dependencies..."
if [ -f "$APP_DIR/requirements.txt" ]; then
    cd "$APP_DIR"
    pip3 install -r requirements.txt --user
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found"
fi

# Step 4: Initialize database
echo "🗄️  Step 4: Initializing database..."
cd "$APP_DIR"
export FLASK_ENV=production
export DATABASE_PATH=$DB_PATH

python3 -c "
try:
    from app import create_app
    from models import db
    app = create_app('production')
    with app.app_context():
        db.create_all()
        print('✅ Database initialized')
except Exception as e:
    print(f'⚠️  Database init: {e}')
"

# Step 5: Create systemd service
echo "🔧 Step 5: Creating systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=SmartGardenHub Flask Application
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
Environment="DATABASE_PATH=$DB_PATH"
Environment="BACKUP_DIR=$BACKUP_DIR"
Environment="PORT=$PORT"
ExecStart=/usr/bin/python3 -m gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 --access-logfile $APP_DIR/logs/access.log --error-logfile $APP_DIR/logs/error.log app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo "✅ Systemd service created"

# Step 6: Setup automatic backups
echo "⏰ Step 6: Setting up automatic backups..."
cat > "$APP_DIR/backup_cron.sh" << 'EOFBACKUP'
#!/bin/bash
cd /var/www/saroyarsir
export FLASK_ENV=production
export DATABASE_PATH=/var/www/saroyarsir/smartgardenhub.db
python3 backup_database.py >> logs/backup_cron.log 2>&1
EOFBACKUP

chmod +x "$APP_DIR/backup_cron.sh"

# Add to crontab
CRON_JOB="0 2 * * 0 cd $APP_DIR && ./backup_cron.sh"
(crontab -l 2>/dev/null | grep -v "backup_cron.sh"; echo "$CRON_JOB") | crontab -
echo "✅ Automatic backups configured"

# Step 7: Start the application
echo "🚀 Step 7: Starting application..."
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME
sleep 3

echo ""
echo "======================================================================"
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "📊 Application Status:"
sudo systemctl status $APP_NAME --no-pager -l | head -15
echo ""
echo "📋 Quick Reference:"
echo "   URL: http://your-server-ip:$PORT"
echo "   Database: $DB_PATH"
echo "   Logs: sudo journalctl -u $APP_NAME -f"
echo "   Restart: sudo systemctl restart $APP_NAME"
echo ""
echo "======================================================================"
