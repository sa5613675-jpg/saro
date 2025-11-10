# 🚀 Quick Start - Online MCQ Exam System

## For VPS Deployment (Copy & Paste)

```bash
# Step 1: Pull latest code
cd /var/www/saroyarsir
git pull origin main

# Step 2: Activate environment
source venv/bin/activate

# Step 3: Run migration
python migrate_add_online_exams.py

# Step 4: Restart server
sudo systemctl restart gunicorn

# Step 5: Test
python test_online_exams.py

# Done! ✅
```

## Teacher Quick Start

1. Login: http://your-domain.com
2. Username: `01762602056`
3. Password: `sir@123@`
4. Click: **"Online MCQ Exams"** in sidebar
5. Click: **"Create New Exam"** button
6. Fill form and add questions
7. Click: **"Create Exam"**

## Student Quick Start

1. Login: http://your-domain.com
2. Username: `guardian_phone` (e.g., 01700000001)
3. Password: `student123`
4. Click: **"Online Exams"** in sidebar
5. Click: **"Start Exam"** on available exam
6. Answer questions (auto-saves)
7. Click: **"Submit Exam"** or wait for timer
8. View results with explanations

## Common Commands

```bash
# Check if app loads
python -c "from app import create_app; app = create_app('production'); print('OK')"

# Test exam system
python test_online_exams.py

# Check database
sqlite3 smartgardenhub.db
sqlite> .tables
sqlite> SELECT COUNT(*) FROM online_exams;
sqlite> SELECT COUNT(*) FROM exam_questions;
sqlite> SELECT COUNT(*) FROM student_exam_attempts;
sqlite> .exit

# View logs
sudo journalctl -u gunicorn -n 50 --no-pager

# Restart service
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

## Troubleshooting One-Liners

```bash
# App won't start
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 100 --no-pager

# Migration error
python migrate_add_online_exams.py

# Database locked
sudo systemctl stop gunicorn
python migrate_add_online_exams.py
sudo systemctl start gunicorn

# Need to reset
# (WARNING: Deletes all exam data)
sqlite3 smartgardenhub.db "DROP TABLE IF EXISTS online_exams;"
sqlite3 smartgardenhub.db "DROP TABLE IF EXISTS exam_questions;"
sqlite3 smartgardenhub.db "DROP TABLE IF EXISTS student_exam_attempts;"
python migrate_add_online_exams.py
```

## File Locations

```
/var/www/saroyarsir/
├── models.py                                    # Database models
├── routes/simple_online_exams.py                # API routes
├── templates/templates/
│   ├── dashboard_teacher.html                   # Teacher dashboard
│   ├── dashboard_student.html                   # Student dashboard
│   └── partials/
│       ├── simple_online_exams_teacher.html     # Teacher UI
│       └── simple_online_exams_student.html     # Student UI
├── migrate_add_online_exams.py                  # Migration
├── test_online_exams.py                         # Test script
├── ONLINE_EXAM_DEPLOYMENT.md                    # Full guide
└── ONLINE_EXAM_SUMMARY.md                       # Summary
```

## API Test (curl)

```bash
# Get all exams (as teacher)
curl -H "Cookie: session=..." http://localhost:5000/api/simple-exams/api/simple-exams

# Get student exams
curl -H "Cookie: session=..." http://localhost:5000/api/simple-exams/api/my-exams
```

## Success Indicators

✅ Migration shows: "✅ Online Exam System tables created successfully!"  
✅ Test shows: "✅ All tests passed!"  
✅ Gunicorn status: "active (running)"  
✅ Teacher can see "Online MCQ Exams" menu  
✅ Student can see "Online Exams" menu  
✅ No errors in `sudo journalctl -u gunicorn`

## Git Status

```bash
# Check current branch
git branch

# Pull latest
git pull origin main

# View recent commits
git log --oneline -5

# Should see:
# ac7e3f0 Add comprehensive summary for Online Exam System
# f71c3fa Add test script for Online Exam System
# 8683bc9 Add deployment guide for Online MCQ Exam System
# 35dd0b8 Add complete Online MCQ Exam System
```

## Need Help?

1. Read `ONLINE_EXAM_DEPLOYMENT.md` for full guide
2. Read `ONLINE_EXAM_SUMMARY.md` for complete overview
3. Run `python test_online_exams.py` to verify system
4. Check logs: `sudo journalctl -u gunicorn -n 100`

---

**Last Updated**: November 10, 2025  
**Status**: ✅ Production Ready
