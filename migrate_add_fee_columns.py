"""
Add exam_fee and other_fee columns to fees table
"""
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    """Add exam_fee and other_fee columns"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Adding exam_fee and other_fee columns to fees table...")
            
            # Check if columns already exist
            result = db.session.execute(text("PRAGMA table_info(fees)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'exam_fee' not in columns:
                db.session.execute(text(
                    "ALTER TABLE fees ADD COLUMN exam_fee DECIMAL(10, 2) DEFAULT 0.00"
                ))
                print("✅ Added exam_fee column")
            else:
                print("ℹ️  exam_fee column already exists")
            
            if 'other_fee' not in columns:
                db.session.execute(text(
                    "ALTER TABLE fees ADD COLUMN other_fee DECIMAL(10, 2) DEFAULT 0.00"
                ))
                print("✅ Added other_fee column")
            else:
                print("ℹ️  other_fee column already exists")
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate()
