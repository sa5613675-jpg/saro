#!/bin/bash#!/bin/bash

## SmartGardenHub VPS Deployment Script

# VPS Deployment Script for SmartGardenHub# Run this on your VPS at /var/www/saroyarsir

# Database: /var/www/saroyarsir/smartgardenhub.db

# Port: 8001set -e  # Exit on error

#

echo "🚀 SmartGardenHub VPS Deployment Script"

set -e  # Exit on errorecho "========================================"



echo "======================================================================"# Colors for output

echo "  SMARTGARDENHUB VPS DEPLOYMENT"RED='\033[0;31m'

echo "======================================================================"GREEN='\033[0;32m'

echo ""YELLOW='\033[1;33m'

NC='\033[0m' # No Color

# Configuration

APP_DIR="/var/www/saroyarsir"# Configuration

DB_PATH="/var/www/saroyarsir/smartgardenhub.db"PROJECT_DIR="/var/www/saroyarsir"

BACKUP_DIR="/var/www/saroyarsir/backups"VENV_DIR="$PROJECT_DIR/venv"

PORT=8001SERVICE_NAME="saro"

APP_NAME="smartgardenhub"

echo -e "${YELLOW}Step 1: Stopping existing services...${NC}"

echo "📋 Configuration:"pkill -f "flask run" || true

echo "   App Directory: $APP_DIR"pkill -f "python run.py" || true

echo "   Database: $DB_PATH"pkill -f "gunicorn" || true

echo "   Backup Directory: $BACKUP_DIR"sudo systemctl stop $SERVICE_NAME 2>/dev/null || true

echo "   Port: $PORT"

echo ""echo -e "${GREEN}✓ Services stopped${NC}"



# Step 1: Create necessary directoriesecho -e "${YELLOW}Step 2: Navigating to project directory...${NC}"

echo "📁 Step 1: Creating directories..."cd $PROJECT_DIR

sudo mkdir -p "$APP_DIR"echo -e "${GREEN}✓ Current directory: $(pwd)${NC}"

sudo mkdir -p "$BACKUP_DIR"

sudo mkdir -p "$APP_DIR/logs"echo -e "${YELLOW}Step 3: Pulling latest code from GitHub...${NC}"

sudo mkdir -p "$APP_DIR/instance"git fetch origin

sudo mkdir -p "$APP_DIR/static/uploads"git pull origin main

sudo mkdir -p "$APP_DIR/flask_session"echo -e "${GREEN}✓ Code updated${NC}"



echo "✅ Directories created"echo -e "${YELLOW}Step 4: Activating virtual environment...${NC}"

if [ ! -d "$VENV_DIR" ]; then

# Step 2: Set proper permissions    echo "Creating virtual environment..."

echo "🔒 Step 2: Setting permissions..."    python3 -m venv venv

sudo chown -R $USER:$USER "$APP_DIR"fi

sudo chmod -R 755 "$APP_DIR"source $VENV_DIR/bin/activate

sudo chmod -R 775 "$BACKUP_DIR"echo -e "${GREEN}✓ Virtual environment activated${NC}"

sudo chmod -R 775 "$APP_DIR/instance"

sudo chmod -R 775 "$APP_DIR/logs"echo -e "${YELLOW}Step 5: Upgrading pip...${NC}"

sudo chmod -R 775 "$APP_DIR/flask_session"pip install --upgrade pip

echo -e "${GREEN}✓ Pip upgraded${NC}"

echo "✅ Permissions set"

echo -e "${YELLOW}Step 6: Installing dependencies...${NC}"

# Step 3: Install Python dependenciespip install -r requirements.txt

echo "📦 Step 3: Installing Python dependencies..."pip install gunicorn

if [ -f "$APP_DIR/requirements.txt" ]; thenecho -e "${GREEN}✓ Dependencies installed${NC}"

    cd "$APP_DIR"

    pip3 install -r requirements.txt --userecho -e "${YELLOW}Step 7: Setting up environment file...${NC}"

    echo "✅ Dependencies installed"if [ ! -f ".env" ]; then

else    echo "Creating .env from template..."

    echo "⚠️  requirements.txt not found in $APP_DIR"    cp .env.example .env

fi    echo -e "${RED}⚠️  IMPORTANT: Edit .env file with your API keys!${NC}"

    echo "   nano .env"

# Step 4: Create .env file (if not exists)else

if [ ! -f "$APP_DIR/.env" ]; then    echo -e "${GREEN}✓ .env file already exists${NC}"

    echo "⚙️  Step 4: Creating .env file..."fi

    cat > "$APP_DIR/.env" << EOF

# Production Environment Configurationecho -e "${YELLOW}Step 8: Setting up database...${NC}"

FLASK_ENV=productionpython create_default_users.py 2>/dev/null || echo "Default users may already exist"

DEBUG=Falseecho -e "${GREEN}✓ Database ready${NC}"



# Database Configurationecho -e "${YELLOW}Step 9: Creating systemd service...${NC}"

DATABASE_PATH=$DB_PATHsudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF

BACKUP_DIR=$BACKUP_DIR[Unit]

Description=SmartGardenHub Flask Application

# Server ConfigurationAfter=network.target

PORT=$PORT

HOST=0.0.0.0[Service]

Type=notify

# SecurityUser=root

SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')WorkingDirectory=$PROJECT_DIR

Environment="PATH=$VENV_DIR/bin"

# SMS Configuration (Update with your credentials)ExecStart=$VENV_DIR/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - "app:create_app()"

SMS_API_KEY=gsOKLO6XtKsANCvgPHNtExecReload=/bin/kill -s HUP \$MAINPID

SMS_SENDER_ID=8809617628909KillMode=mixed

TimeoutStopSec=5

EOFPrivateTmp=true

    chmod 600 "$APP_DIR/.env"Restart=always

    echo "✅ .env file created"

else[Install]

    echo "⚙️  Step 4: .env file already exists, skipping..."WantedBy=multi-user.target

fiEOF

echo -e "${GREEN}✓ Service file created${NC}"

# Step 5: Initialize database

echo "🗄️  Step 5: Initializing database..."echo -e "${YELLOW}Step 10: Enabling and starting service...${NC}"

cd "$APP_DIR"sudo systemctl daemon-reload

export FLASK_ENV=productionsudo systemctl enable $SERVICE_NAME

export DATABASE_PATH=$DB_PATHsudo systemctl start $SERVICE_NAME

echo -e "${GREEN}✓ Service started${NC}"

python3 << 'EOFPYTHON'

try:echo ""

    from app import create_appecho "========================================"

    from models import dbecho -e "${GREEN}🎉 Deployment Complete!${NC}"

    echo "========================================"

    app = create_app('production')echo ""

    with app.app_context():echo "📊 Service Status:"

        db.create_all()sudo systemctl status $SERVICE_NAME --no-pager

        print('✅ Database initialized successfully')echo ""

except Exception as e:echo "📝 Useful Commands:"

    print(f'⚠️  Database initialization: {e}')echo "  View logs:        sudo journalctl -u $SERVICE_NAME -f"

EOFPYTHONecho "  Restart service:  sudo systemctl restart $SERVICE_NAME"

echo "  Stop service:     sudo systemctl stop $SERVICE_NAME"

# Step 6: Create/Update systemd serviceecho "  Check status:     sudo systemctl status $SERVICE_NAME"

echo "🔧 Step 6: Creating systemd service..."echo ""

sudo bash -c "cat > /etc/systemd/system/$APP_NAME.service" << EOFecho "🌐 Application URL: http://your-vps-ip:5000"

[Unit]echo ""

Description=SmartGardenHub Flask Applicationecho -e "${YELLOW}⚠️  Don't forget to:${NC}"

After=network.targetecho "  1. Edit .env file with your actual API keys"

echo "  2. Configure your firewall to allow port 5000"

[Service]echo "  3. Set up Nginx as reverse proxy (recommended)"

Type=exececho ""

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

# Step 7: Setup automatic backups (cron)
echo "⏰ Step 7: Setting up automatic backups..."
cat > "$APP_DIR/backup_cron.sh" << 'EOFBACKUP'
#!/bin/bash
# Automatic backup script
cd /var/www/saroyarsir
export FLASK_ENV=production
export DATABASE_PATH=/var/www/saroyarsir/smartgardenhub.db
python3 backup_database.py >> logs/backup_cron.log 2>&1
EOFBACKUP

chmod +x "$APP_DIR/backup_cron.sh"

# Add to crontab (weekly Sunday 2 AM)
CRON_JOB="0 2 * * 0 cd $APP_DIR && ./backup_cron.sh"
(crontab -l 2>/dev/null | grep -v "backup_cron.sh"; echo "$CRON_JOB") | crontab -

echo "✅ Automatic backups configured (Every Sunday at 2:00 AM)"

# Step 8: Start the application
echo "🚀 Step 8: Starting application..."
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

sleep 3

echo ""
echo "======================================================================"
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "📊 Application Status:"
sudo systemctl status $APP_NAME --no-pager -l | head -20
echo ""
echo "📋 Configuration:"
echo "   URL: http://your-server-ip:$PORT"
echo "   Database: $DB_PATH"
echo "   Backups: $BACKUP_DIR"
echo "   Logs: $APP_DIR/logs/"
echo ""
echo "🔧 Management Commands:"
echo "   Status:  sudo systemctl status $APP_NAME"
echo "   Start:   sudo systemctl start $APP_NAME"
echo "   Stop:    sudo systemctl stop $APP_NAME"
echo "   Restart: sudo systemctl restart $APP_NAME"
echo "   Logs:    sudo journalctl -u $APP_NAME -f"
echo "   Backup:  cd $APP_DIR && python3 backup_database.py"
echo ""
echo "🔍 Check application:"
echo "   curl http://localhost:$PORT/health"
echo ""
echo "======================================================================"
