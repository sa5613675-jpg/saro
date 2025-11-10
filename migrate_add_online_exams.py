#!/usr/bin/env python3
"""
Migration: Add Online Exam System Tables
Creates tables for online MCQ exams with questions and student attempts
"""
import sys
from app import create_app
from models import db, OnlineExam, ExamQuestion, StudentExamAttempt

def migrate():
    """Add online exam tables"""
    app = create_app('production')
    
    with app.app_context():
        print("📚 Creating Online Exam System tables...")
        
        # Create tables using SQLAlchemy models
        try:
            # Create all new tables
            db.create_all()
            
            print("✅ Created online_exams table")
            print("✅ Created exam_questions table")
            print("✅ Created student_exam_attempts table")
            
            db.session.commit()
            print("\n✅ Online Exam System tables created successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error creating tables: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    try:
        success = migrate()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
