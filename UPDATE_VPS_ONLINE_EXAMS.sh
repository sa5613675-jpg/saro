#!/bin/bash
# Update VPS with Online Exam Fixes
# Run this on your VPS server

echo "=========================================="
echo "Updating Online Exam System on VPS"
echo "=========================================="

cd /var/www/saroyarsir || exit 1

# Backup current state
echo "1. Creating backup..."
cp smartgardenhub.db smartgardenhub.db.backup.$(date +%Y%m%d_%H%M%S)

# Pull latest changes
echo "2. Pulling latest code from GitHub..."
git pull origin main

# Activate virtual environment
echo "3. Activating virtual environment..."
source venv/bin/activate

# Install any new dependencies (if needed)
echo "4. Checking dependencies..."
pip install -q -r requirements.txt

# Stop the service
echo "5. Stopping smartgardenhub service..."
sudo systemctl stop smartgardenhub

# Clean up any stale PID files
echo "6. Cleaning up PID files..."
rm -f /tmp/smartgarden-hub.pid

# Restart the service
echo "7. Starting smartgardenhub service..."
sudo systemctl start smartgardenhub

# Wait a moment
sleep 3

# Check status
echo "8. Checking service status..."
sudo systemctl status smartgardenhub --no-pager

echo ""
echo "=========================================="
echo "Update Complete!"
echo "=========================================="
echo ""
echo "Modified files:"
echo "  - routes/simple_online_exams.py (fixed question ordering)"
echo "  - templates/templates/partials/online_exam_list.html (added working interface)"
echo ""
echo "Test the changes:"
echo "  1. Login as student: 01700000001 / 123456"
echo "  2. Click 'Online Exam' in navigation"
echo "  3. You should see 'Physics Chapter 1 - Demo Exam'"
echo "  4. Start the exam and verify questions are ordered 1-10"
echo ""
echo "If you need to create the demo exam on VPS:"
echo "  cd /var/www/saroyarsir"
echo "  source venv/bin/activate"
echo "  python create_demo_online_exam.py"
echo ""
