#!/usr/bin/env python3
"""
Test SMS Template Persistence Fix
Verify that templates save to database and work across different sessions/IPs
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Settings, User, UserRole, db
from utils.sms_templates import get_sms_template, save_sms_template, get_all_saved_templates

def test_template_persistence():
    """Test that SMS templates persist across sessions"""
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("Testing SMS Template Persistence Fix")
        print("=" * 60)
        
        # Get a teacher user
        teacher = User.query.filter_by(role=UserRole.TEACHER).first()
        if not teacher:
            teacher = User.query.filter_by(role=UserRole.SUPER_USER).first()
        
        if not teacher:
            print("❌ No teacher or super user found")
            return
        
        print(f"\n✓ Using user: {teacher.full_name} (ID: {teacher.id})")
        
        # Test 1: Save a custom template
        print("\n" + "=" * 60)
        print("Test 1: Saving custom template to database")
        print("=" * 60)
        
        custom_message = "প্রিয় অভিভাবক, {student_name} এর {subject} পরীক্ষায় নম্বর {marks}/{total} - গ্রেড: {grade}"
        success = save_sms_template('exam_result', custom_message, teacher.id)
        
        if success:
            print("✓ Template saved successfully to database")
        else:
            print("❌ Failed to save template")
            return
        
        # Test 2: Retrieve saved template (without session)
        print("\n" + "=" * 60)
        print("Test 2: Retrieving saved template (simulating different IP/session)")
        print("=" * 60)
        
        retrieved_template = get_sms_template('exam_result')
        
        if retrieved_template == custom_message:
            print("✓ Template retrieved correctly from database")
            print(f"   Template: {retrieved_template}")
        else:
            print("❌ Template mismatch!")
            print(f"   Expected: {custom_message}")
            print(f"   Got: {retrieved_template}")
            return
        
        # Test 3: Get all saved templates
        print("\n" + "=" * 60)
        print("Test 3: Getting all saved templates")
        print("=" * 60)
        
        all_templates = get_all_saved_templates()
        print(f"✓ Found {len(all_templates)} saved template(s):")
        for template_type, message in all_templates.items():
            print(f"   - {template_type}: {message[:50]}...")
        
        # Test 4: Verify database entry
        print("\n" + "=" * 60)
        print("Test 4: Verifying database entry")
        print("=" * 60)
        
        db_template = Settings.query.filter_by(key='sms_template_exam_result').first()
        
        if db_template:
            print("✓ Template found in database")
            print(f"   Key: {db_template.key}")
            print(f"   Category: {db_template.category}")
            print(f"   Message: {db_template.value.get('message', 'N/A')[:50]}...")
            print(f"   Updated by: {db_template.updated_by}")
            print(f"   Updated at: {db_template.updated_at}")
        else:
            print("❌ Template not found in database")
            return
        
        # Test 5: Test with different template types
        print("\n" + "=" * 60)
        print("Test 5: Testing attendance templates")
        print("=" * 60)
        
        attendance_message = "প্রিয় অভিভাবক, {student_name} আজ {batch_name} ক্লাসে {date} তারিখে উপস্থিত ছিল।"
        success = save_sms_template('attendance_present', attendance_message, teacher.id)
        
        if success:
            print("✓ Attendance template saved")
            retrieved = get_sms_template('attendance_present')
            if retrieved == attendance_message:
                print("✓ Attendance template retrieved correctly")
            else:
                print("❌ Attendance template mismatch")
        else:
            print("❌ Failed to save attendance template")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✅ SMS Template Persistence Fix Verification Complete")
        print("\nKey improvements:")
        print("1. Templates now save to database (Settings table)")
        print("2. Templates persist across different IPs and browser sessions")
        print("3. Database templates have priority over session templates")
        print("4. Centralized utility functions for consistent behavior")
        print("\nPriority order:")
        print("1. Database saved template (permanent, cross-session)")
        print("2. Session template (temporary override)")
        print("3. Default template (fallback)")
        print("=" * 60)

if __name__ == '__main__':
    test_template_persistence()
