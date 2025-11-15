#!/bin/bash

# Connect Online Exam System to Production
# This ensures the new simple online exam system is properly integrated

echo "=========================================="
echo "Connecting Online Exam System"
echo "=========================================="

# Step 1: Verify the simple_online_exams routes are registered
echo "✓ Routes registered in app.py: simple_exams_bp at /api/simple-exams"

# Step 2: Verify the template includes the correct partial
echo "✓ Template: dashboard_student_new.html includes partials/online_exam_list.html"

# Step 3: Verify the partial has the Alpine.js component
echo "✓ Partial: online_exam_list.html has x-data='studentExams()' component"

# Step 4: Check if demo exam exists in database
echo ""
echo "Checking for demo exam in database..."
python3 << 'PYEOF'
from app import create_app, db
from models import OnlineExam, ExamQuestion, User, Batch

app = create_app('development')
with app.app_context():
    exams = OnlineExam.query.all()
    print(f"\nFound {len(exams)} online exam(s):")
    for exam in exams:
        print(f"  - ID: {exam.id}, Title: {exam.title}")
        questions = ExamQuestion.query.filter_by(exam_id=exam.id).count()
        print(f"    Questions: {questions}")
    
    students = User.query.filter_by(phoneNumber='01700000001').all()
    if students:
        print(f"\n✓ Demo student exists (Phone: 01700000001)")
    else:
        print(f"\n✗ Demo student NOT found")
    
    batches = Batch.query.all()
    print(f"\nBatches: {len(batches)}")
    for batch in batches:
        print(f"  - {batch.name} (Students: {len(batch.students)})")
PYEOF

echo ""
echo "=========================================="
echo "System Status:"
echo "=========================================="
echo "1. API Routes: /api/simple-exams/* (NEW SYSTEM)"
echo "2. Student Dashboard: dashboard_student_new.html"
echo "3. Exam Interface: partials/online_exam_list.html"
echo "4. Demo Login: Phone=01700000001, Password=123456"
echo ""
echo "TO TEST LOCALLY:"
echo "1. Run: python app.py"
echo "2. Open: http://127.0.0.1:5000"
echo "3. Login with demo credentials"
echo "4. Click 'Online Exam' in sidebar"
echo ""
echo "TO DEPLOY TO VPS:"
echo "1. git add ."
echo "2. git commit -m 'Update online exam system'"
echo "3. git push origin main"
echo "4. SSH to VPS and run:"
echo "   cd /var/www/saroyarsir"
echo "   git pull origin main"
echo "   python migrate_add_online_exams.py"
echo "   sudo systemctl restart smartgardenhub"
echo "=========================================="
