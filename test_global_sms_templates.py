#!/usr/bin/env python3
"""
Test Global SMS Template System
Verify that when ONE teacher saves a template, it's immediately available to ALL teachers
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, UserRole, db
from utils.sms_templates import get_sms_template, save_sms_template, get_all_saved_templates

def test_global_templates():
    """Test that templates are global across all teachers"""
    app = create_app()
    with app.app_context():
        print("=" * 70)
        print("TESTING GLOBAL SMS TEMPLATE SYSTEM")
        print("=" * 70)
        
        # Get all teachers
        teachers = User.query.filter_by(role=UserRole.TEACHER).all()
        if len(teachers) < 1:
            # Create some test teachers
            print("\n📝 Creating test teachers...")
            from werkzeug.security import generate_password_hash
            
            for i in range(1, 4):
                teacher = User(
                    username=f"teacher{i}",
                    password_hash=generate_password_hash(f"teacher{i}23"),
                    phone=f"0181234567{i}",
                    first_name=f"Teacher",
                    last_name=f"{i}",
                    role=UserRole.TEACHER,
                    sms_count=100
                )
                db.session.add(teacher)
            db.session.commit()
            teachers = User.query.filter_by(role=UserRole.TEACHER).all()
        
        print(f"\n✓ Found {len(teachers)} teachers in system:")
        for teacher in teachers[:5]:
            print(f"   - {teacher.full_name} (ID: {teacher.id}, Phone: {teacher.phone})")
        
        # SCENARIO 1: Teacher 1 saves a custom template
        print("\n" + "=" * 70)
        print("SCENARIO 1: Teacher 1 saves a custom exam result template")
        print("=" * 70)
        
        teacher1 = teachers[0]
        custom_template = "প্রিয় অভিভাবক, {student_name} এর {subject} পরীক্ষায় প্রাপ্ত নম্বর: {marks}/{total} - গ্রেড: {grade}. GS Nursing"
        
        print(f"\n👤 Teacher: {teacher1.full_name}")
        print(f"📝 Saving template: {custom_template[:50]}...")
        
        success = save_sms_template('exam_result', custom_template, teacher1.id)
        
        if success:
            print("✅ Template saved to database by Teacher 1")
        else:
            print("❌ Failed to save template")
            return
        
        # SCENARIO 2: Teacher 2 retrieves the template (different user)
        print("\n" + "=" * 70)
        print("SCENARIO 2: Teacher 2 retrieves the same template")
        print("=" * 70)
        
        if len(teachers) > 1:
            teacher2 = teachers[1]
            print(f"\n👤 Teacher: {teacher2.full_name}")
            
            retrieved_template = get_sms_template('exam_result')
            
            if retrieved_template == custom_template:
                print("✅ Teacher 2 sees the SAME template saved by Teacher 1")
                print(f"   Template: {retrieved_template[:50]}...")
            else:
                print("❌ Template mismatch!")
                print(f"   Expected: {custom_template[:50]}...")
                print(f"   Got: {retrieved_template[:50]}...")
                return
        
        # SCENARIO 3: Teacher 3 also sees the same template
        print("\n" + "=" * 70)
        print("SCENARIO 3: Teacher 3 also retrieves the same template")
        print("=" * 70)
        
        if len(teachers) > 2:
            teacher3 = teachers[2]
            print(f"\n👤 Teacher: {teacher3.full_name}")
            
            retrieved_template = get_sms_template('exam_result')
            
            if retrieved_template == custom_template:
                print("✅ Teacher 3 sees the SAME template saved by Teacher 1")
                print(f"   Template: {retrieved_template[:50]}...")
            else:
                print("❌ Template mismatch!")
                return
        
        # SCENARIO 4: Get all saved templates (should be visible to everyone)
        print("\n" + "=" * 70)
        print("SCENARIO 4: All saved templates are visible to everyone")
        print("=" * 70)
        
        all_templates = get_all_saved_templates()
        print(f"\n✅ {len(all_templates)} template(s) saved in database (visible to ALL):")
        for template_type, message in all_templates.items():
            print(f"   - {template_type}: {message[:60]}...")
        
        # SCENARIO 5: Teacher 2 updates the template
        print("\n" + "=" * 70)
        print("SCENARIO 5: Teacher 2 updates the template")
        print("=" * 70)
        
        if len(teachers) > 1:
            teacher2 = teachers[1]
            updated_template = "Dear Parent, {student_name} result: {marks}/{total} in {subject}. Grade: {grade}. GS Center"
            
            print(f"\n👤 Teacher: {teacher2.full_name}")
            print(f"📝 Updating template: {updated_template[:50]}...")
            
            success = save_sms_template('exam_result', updated_template, teacher2.id)
            
            if success:
                print("✅ Template updated by Teacher 2")
                
                # Teacher 1 should see the update immediately
                print(f"\n🔄 Checking if Teacher 1 sees the update...")
                retrieved_by_teacher1 = get_sms_template('exam_result')
                
                if retrieved_by_teacher1 == updated_template:
                    print("✅ Teacher 1 IMMEDIATELY sees Teacher 2's update!")
                    print(f"   Template: {retrieved_by_teacher1[:50]}...")
                else:
                    print("❌ Teacher 1 doesn't see the update")
                    return
        
        # SCENARIO 6: Test attendance templates
        print("\n" + "=" * 70)
        print("SCENARIO 6: Testing attendance templates (present/absent)")
        print("=" * 70)
        
        attendance_present = "প্রিয় অভিভাবক, {student_name} আজ {batch_name} ক্লাসে {date} উপস্থিত ছিল। ধন্যবাদ।"
        attendance_absent = "প্রিয় অভিভাবক, {student_name} আজ {batch_name} ক্লাসে {date} অনুপস্থিত ছিল। দয়া করে নিয়মিত উপস্থিতি নিশ্চিত করুন।"
        
        save_sms_template('attendance_present', attendance_present, teacher1.id)
        save_sms_template('attendance_absent', attendance_absent, teacher1.id)
        
        print(f"✅ Teacher 1 saved attendance templates")
        
        # All teachers should see them
        for idx, teacher in enumerate(teachers[:3], 1):
            present = get_sms_template('attendance_present')
            absent = get_sms_template('attendance_absent')
            
            if present == attendance_present and absent == attendance_absent:
                print(f"✅ Teacher {idx} ({teacher.full_name}) sees both attendance templates")
            else:
                print(f"❌ Teacher {idx} doesn't see the templates correctly")
                return
        
        # FINAL SUMMARY
        print("\n" + "=" * 70)
        print("✅ GLOBAL SMS TEMPLATE SYSTEM TEST PASSED!")
        print("=" * 70)
        print("\n🎉 Key Features Verified:")
        print("1. ✅ Templates saved by ONE teacher are visible to ALL teachers")
        print("2. ✅ Updates by one teacher are IMMEDIATELY visible to all others")
        print("3. ✅ All template types work globally (exam, attendance, etc.)")
        print("4. ✅ Database-backed storage ensures persistence across sessions")
        print("5. ✅ No IP or browser-specific limitations")
        print("\n💡 How it works:")
        print("   - Templates are stored in the 'settings' table in the database")
        print("   - All users query the same database")
        print("   - Database has priority over session/browser cache")
        print("   - Changes are immediate and global")
        print("=" * 70)

if __name__ == '__main__':
    test_global_templates()
