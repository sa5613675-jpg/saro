#!/usr/bin/env python3
"""
Create demo online exam for testing
"""
import sys
from datetime import datetime
from app import create_app, db
from models import User, Batch, OnlineExam, ExamQuestion, UserRole
from werkzeug.security import generate_password_hash

# Create app instance
app = create_app('development')

def create_demo_exam():
    with app.app_context():
        # Check if demo student exists
        demo_student = User.query.filter_by(phoneNumber='01700000001').first()
        if not demo_student:
            print("Creating demo student account...")
            demo_student = User(
                first_name='Demo',
                last_name='Student',
                phoneNumber='01700000001',
                password_hash=generate_password_hash('123456'),
                role=UserRole.STUDENT,
                guardian_name='Demo Guardian',
                guardian_phone='01700000002'
            )
            db.session.add(demo_student)
            db.session.commit()
            print(f"✓ Created demo student - Phone: 01700000001, Password: 123456")
        else:
            print(f"✓ Demo student already exists - Phone: 01700000001, Password: 123456")
        
        # Check if demo batch exists
        demo_batch = Batch.query.filter_by(name='Physics Batch').first()
        if not demo_batch:
            print("Creating demo batch...")
            demo_batch = Batch(
                name='Physics Batch',
                subject='Physics',
                start_date=datetime.now().date()
            )
            db.session.add(demo_batch)
            db.session.commit()
            print(f"✓ Created demo batch: Physics Batch")
        else:
            print(f"✓ Demo batch already exists: Physics Batch")
        
        # Add student to batch if not already enrolled
        if demo_student not in demo_batch.students:
            demo_batch.students.append(demo_student)
            db.session.commit()
            print(f"✓ Enrolled demo student in Physics Batch")
        
        # Check if demo exam exists
        demo_exam = OnlineExam.query.filter_by(title='Physics Chapter 1 - Demo Exam').first()
        if demo_exam:
            print("Demo exam already exists. Deleting old one...")
            # Delete old questions
            ExamQuestion.query.filter_by(exam_id=demo_exam.id).delete()
            db.session.delete(demo_exam)
            db.session.commit()
        
        print("Creating demo online exam...")
        exam = OnlineExam(
            batch_id=demo_batch.id,
            title='Physics Chapter 1 - Demo Exam',
            class_name='HSC 2nd Year',
            book_name='Physics 2nd Paper',
            chapter_name='Chapter 1: Electricity and Magnetism',
            duration_minutes=20,  # 20 minutes for demo
            total_questions=10,   # 10 questions for demo
            pass_marks=40,
            created_by=1,  # Admin user
            is_active=True,
            allow_retake=True
        )
        db.session.add(exam)
        db.session.commit()
        print(f"✓ Created exam: {exam.title}")
        
        # Create 10 demo questions
        questions = [
            {
                'question_number': 1,
                'question_text': 'What is the SI unit of electric charge?',
                'option_a': 'Ampere',
                'option_b': 'Coulomb',
                'option_c': 'Volt',
                'option_d': 'Ohm',
                'correct_answer': 'B',
                'explanation': 'The SI unit of electric charge is Coulomb (C), named after Charles-Augustin de Coulomb.'
            },
            {
                'question_number': 2,
                'question_text': 'According to Ohm\'s law, voltage is equal to:',
                'option_a': 'Current × Resistance',
                'option_b': 'Current / Resistance',
                'option_c': 'Resistance / Current',
                'option_d': 'Power × Time',
                'correct_answer': 'A',
                'explanation': 'Ohm\'s law states V = I × R, where V is voltage, I is current, and R is resistance.'
            },
            {
                'question_number': 3,
                'question_text': 'What type of material has very high electrical resistance?',
                'option_a': 'Conductor',
                'option_b': 'Semiconductor',
                'option_c': 'Insulator',
                'option_d': 'Superconductor',
                'correct_answer': 'C',
                'explanation': 'Insulators have very high electrical resistance and do not allow electric current to flow easily.'
            },
            {
                'question_number': 4,
                'question_text': 'The direction of magnetic field lines inside a magnet is:',
                'option_a': 'From North to South',
                'option_b': 'From South to North',
                'option_c': 'Circular',
                'option_d': 'Random',
                'correct_answer': 'B',
                'explanation': 'Inside a magnet, magnetic field lines run from South pole to North pole. Outside, they go from North to South.'
            },
            {
                'question_number': 5,
                'question_text': 'What happens to the resistance of a conductor when temperature increases?',
                'option_a': 'Increases',
                'option_b': 'Decreases',
                'option_c': 'Remains constant',
                'option_d': 'Becomes zero',
                'correct_answer': 'A',
                'explanation': 'For most conductors, resistance increases with temperature due to increased atomic vibrations.'
            },
            {
                'question_number': 6,
                'question_text': 'In a series circuit, the total resistance is:',
                'option_a': 'Sum of all resistances',
                'option_b': 'Product of all resistances',
                'option_c': 'Average of all resistances',
                'option_d': 'Less than the smallest resistance',
                'correct_answer': 'A',
                'explanation': 'In series circuits, total resistance R_total = R1 + R2 + R3 + ... (sum of all resistances).'
            },
            {
                'question_number': 7,
                'question_text': 'Fleming\'s left-hand rule is used to find:',
                'option_a': 'Direction of induced current',
                'option_b': 'Direction of force on current-carrying conductor',
                'option_c': 'Direction of magnetic field',
                'option_d': 'Magnitude of current',
                'correct_answer': 'B',
                'explanation': 'Fleming\'s left-hand rule determines the direction of force on a current-carrying conductor in a magnetic field.'
            },
            {
                'question_number': 8,
                'question_text': 'The unit of electric potential is:',
                'option_a': 'Ampere',
                'option_b': 'Watt',
                'option_c': 'Volt',
                'option_d': 'Joule',
                'correct_answer': 'C',
                'explanation': 'Electric potential is measured in Volts (V), which equals Joules per Coulomb (J/C).'
            },
            {
                'question_number': 9,
                'question_text': 'What is the power dissipated in a resistor carrying current I with resistance R?',
                'option_a': 'I × R',
                'option_b': 'I² × R',
                'option_c': 'I / R',
                'option_d': 'R / I',
                'correct_answer': 'B',
                'explanation': 'Power dissipated P = I²R (or V²/R or V×I), where I is current and R is resistance.'
            },
            {
                'question_number': 10,
                'question_text': 'Electromagnetic induction was discovered by:',
                'option_a': 'Isaac Newton',
                'option_b': 'Michael Faraday',
                'option_c': 'Albert Einstein',
                'option_d': 'James Clerk Maxwell',
                'correct_answer': 'B',
                'explanation': 'Michael Faraday discovered electromagnetic induction in 1831, showing that changing magnetic fields induce electric current.'
            }
        ]
        
        for q_data in questions:
            question = ExamQuestion(
                exam_id=exam.id,
                question_number=q_data['question_number'],
                question_text=q_data['question_text'],
                option_a=q_data['option_a'],
                option_b=q_data['option_b'],
                option_c=q_data['option_c'],
                option_d=q_data['option_d'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data['explanation']
            )
            db.session.add(question)
        
        db.session.commit()
        print(f"✓ Created {len(questions)} questions")
        
        print("\n" + "="*60)
        print("DEMO ONLINE EXAM CREATED SUCCESSFULLY!")
        print("="*60)
        print("\n📱 STUDENT LOGIN CREDENTIALS:")
        print(f"   Phone: 01700000001")
        print(f"   Password: 123456")
        print(f"\n📚 EXAM DETAILS:")
        print(f"   Title: {exam.title}")
        print(f"   Class: {exam.class_name}")
        print(f"   Subject: Physics")
        print(f"   Chapter: {exam.chapter_name}")
        print(f"   Questions: {exam.total_questions}")
        print(f"   Duration: {exam.duration_minutes} minutes")
        print(f"   Pass Marks: {exam.pass_marks}%")
        print(f"   Retake Allowed: {'Yes' if exam.allow_retake else 'No'}")
        print("\n🌐 ACCESS THE APP:")
        print(f"   URL: http://127.0.0.1:5000")
        print("\n✅ TESTING STEPS:")
        print("   1. Login with student credentials")
        print("   2. Click 'Online Exams' in navigation")
        print("   3. Find 'Physics Chapter 1 - Demo Exam'")
        print("   4. Click 'Start Exam' button")
        print("   5. Answer the 10 questions")
        print("   6. Submit and view results with explanations")
        print("="*60 + "\n")

if __name__ == '__main__':
    try:
        create_demo_exam()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
