#!/bin/bash
# VPS Deployment for Online Exam System Fix
# Run this on your VPS at /var/www/saroyarsir

echo "=========================================="
echo "Deploying Online Exam System Updates"
echo "=========================================="

cd /var/www/saroyarsir

echo "Step 1: Pull latest code from GitHub..."
git pull origin main

echo ""
echo "Step 2: Run migration to create online exam tables..."
python3 migrate_add_online_exams.py

echo ""
echo "Step 3: Create demo exam and student..."
python3 create_demo_online_exam.py

echo ""
echo "Step 4: Restart application service..."
sudo systemctl restart smartgardenhub

echo ""
echo "Step 5: Check service status..."
sudo systemctl status smartgardenhub --no-pager

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Demo Student Credentials:"
echo "  Phone: 01700000001"
echo "  Password: 123456"
echo ""
echo "Access your site and:"
echo "1. Login with demo student"
echo "2. Click 'Online Exam' in sidebar"
echo "3. You should see: Physics Chapter 1 - Demo Exam"
echo "=========================================="
