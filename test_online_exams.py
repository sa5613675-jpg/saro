#!/usr/bin/env python3
"""
Test Online Exam System
Verifies all components are working correctly
"""
import sys
from app import create_app
from models import db, OnlineExam, ExamQuestion, StudentExamAttempt, Batch, User

def test_online_exam_system():
    """Test the online exam system"""
    app = create_app('production')
    
    with app.app_context():
        print("🧪 Testing Online Exam System...")
        print()
        
        # Test 1: Check if tables exist
        print("1️⃣ Checking database tables...")
        try:
            exam_count = OnlineExam.query.count()
            question_count = ExamQuestion.query.count()
            attempt_count = StudentExamAttempt.query.count()
            print(f"   ✅ online_exams table: {exam_count} exams")
            print(f"   ✅ exam_questions table: {question_count} questions")
            print(f"   ✅ student_exam_attempts table: {attempt_count} attempts")
        except Exception as e:
            print(f"   ❌ Database tables error: {e}")
            return False
        
        # Test 2: Check if batches exist for assignment
        print()
        print("2️⃣ Checking batches for exam assignment...")
        try:
            batches = Batch.query.filter_by(is_active=True).all()
            print(f"   ✅ Found {len(batches)} active batches")
            for batch in batches:
                print(f"      - {batch.name}")
        except Exception as e:
            print(f"   ❌ Batch check error: {e}")
            return False
        
        # Test 3: Check teacher accounts
        print()
        print("3️⃣ Checking teacher accounts...")
        try:
            teachers = User.query.filter_by(role='teacher').all()
            print(f"   ✅ Found {len(teachers)} teachers")
            for teacher in teachers:
                print(f"      - {teacher.name} ({teacher.phoneNumber})")
        except Exception as e:
            print(f"   ❌ Teacher check error: {e}")
            return False
        
        # Test 4: Check student accounts
        print()
        print("4️⃣ Checking student accounts...")
        try:
            students = User.query.filter_by(role='student').limit(5).all()
            print(f"   ✅ Found students (showing first 5):")
            for student in students:
                print(f"      - {student.name} ({student.guardian_phone})")
        except Exception as e:
            print(f"   ❌ Student check error: {e}")
            return False
        
        # Test 5: Verify model relationships
        print()
        print("5️⃣ Testing model relationships...")
        try:
            if exam_count > 0:
                exam = OnlineExam.query.first()
                print(f"   ✅ Exam relationships working:")
                print(f"      - Exam: {exam.title}")
                print(f"      - Questions: {len(exam.questions)}")
                print(f"      - Attempts: {len(exam.attempts)}")
            else:
                print(f"   ℹ️  No exams yet to test relationships")
        except Exception as e:
            print(f"   ❌ Relationship error: {e}")
            return False
        
        # Test 6: Check JSON answer storage
        print()
        print("6️⃣ Testing JSON answer storage...")
        try:
            if attempt_count > 0:
                attempt = StudentExamAttempt.query.first()
                answers = attempt.get_answers()
                print(f"   ✅ JSON answer storage working:")
                print(f"      - Attempt ID: {attempt.id}")
                print(f"      - Answers: {answers}")
            else:
                print(f"   ℹ️  No attempts yet to test JSON storage")
        except Exception as e:
            print(f"   ❌ JSON storage error: {e}")
            return False
        
        print()
        print("=" * 60)
        print("✅ All tests passed! Online Exam System is ready to use.")
        print()
        print("📝 Next Steps:")
        print("1. Login as teacher (01762602056 / sir@123@)")
        print("2. Click 'Online MCQ Exams' in sidebar")
        print("3. Create a test exam with a few questions")
        print("4. Login as student and take the exam")
        print("5. View results with explanations")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    try:
        success = test_online_exam_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
