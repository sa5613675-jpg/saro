#!/usr/bin/env python3
"""
Fix Teacher Login - Set password for 01762602056
Run this script to ensure teacher can login with sir@123@
"""
import sys
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def fix_teacher_login():
    """Update teacher password"""
    app = create_app('production')
    
    with app.app_context():
        # Find teacher by phone
        phone = '01762602056'
        password = 'sir@123@'
        
        print(f"🔍 Looking for user with phone: {phone}")
        user = User.query.filter_by(phoneNumber=phone).first()
        
        if not user:
            print(f"❌ User not found with phone {phone}")
            return False
        
        print(f"✅ Found user: {user.first_name} {user.last_name} (ID: {user.id}, Role: {user.role.value})")
        
        # Generate password hash
        password_hash = generate_password_hash(password)
        print(f"🔐 Generated password hash: {password_hash[:30]}...")
        
        # Update password
        user.password_hash = password_hash
        db.session.commit()
        
        print(f"✅ Password updated successfully!")
        print(f"\n📱 Login credentials:")
        print(f"   Phone: {phone}")
        print(f"   Password: {password}")
        print(f"\n✅ Teacher can now login!")
        
        return True

if __name__ == '__main__':
    try:
        success = fix_teacher_login()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
