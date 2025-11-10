#!/usr/bin/env python3
"""
Database Restore Script
Restore database from a backup file
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_backup import DatabaseBackupManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def list_backups(backup_manager):
    """List available backups"""
    backups = backup_manager.list_backups()
    
    if not backups:
        print("❌ No backups found in backups/")
        return None
    
    print("\n📋 Available Backups:")
    print("=" * 70)
    for idx, backup in enumerate(backups, 1):
        print(f"{idx}. {backup['name']}")
        print(f"   Size: {backup['size_mb']:.2f} MB")
        print(f"   Created: {backup['created']}")
        print(f"   Age: {backup['age_days']} days")
        print()
    
    return backups

def main():
    """Run database restore"""
    print("=" * 70)
    print("DATABASE RESTORE UTILITY")
    print("=" * 70)
    print("\n⚠️  WARNING: This will replace your current database!")
    print("⚠️  A backup of your current database will be created first.")
    
    # Database path
    db_path = Path('instance/database.db')
    backup_manager = DatabaseBackupManager(str(db_path), 'backups')
    
    # List available backups
    backups = list_backups(backup_manager)
    
    if not backups:
        return 1
    
    # Ask user to select backup
    print("=" * 70)
    try:
        selection = input("\nEnter backup number to restore (or 'q' to quit): ").strip()
        
        if selection.lower() == 'q':
            print("Cancelled.")
            return 0
        
        backup_idx = int(selection) - 1
        
        if backup_idx < 0 or backup_idx >= len(backups):
            print("❌ Invalid selection")
            return 1
        
        selected_backup = backups[backup_idx]
        
    except ValueError:
        print("❌ Invalid input")
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 0
    
    # Confirm restoration
    print(f"\n📦 Selected backup: {selected_backup['name']}")
    print(f"   Size: {selected_backup['size_mb']:.2f} MB")
    print(f"   Created: {selected_backup['created']}")
    
    confirm = input("\n⚠️  Are you sure you want to restore? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Cancelled.")
        return 0
    
    # Perform restore
    print(f"\n🔄 Restoring database from backup...")
    
    success = backup_manager.restore_backup(
        backup_path=selected_backup['path'],
        restore_to=db_path
    )
    
    if success:
        print(f"\n✅ Database restored successfully!")
        print(f"   From: {selected_backup['name']}")
        print(f"   To: {db_path}")
        print(f"\n   A backup of your previous database was saved to:")
        print(f"   {db_path}.before_restore")
        print("\n=" * 70)
        return 0
    else:
        print(f"\n❌ Restore failed!")
        print("   Check logs for details.")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    exit(main())
