#!/usr/bin/env python3
"""
Manual Database Backup Script
Run this script to create an immediate database backup
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_backup import DatabaseBackupManager
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Run manual backup"""
    print("=" * 70)
    print("DATABASE MANUAL BACKUP")
    print("=" * 70)
    
    # Database path
    db_path = Path('instance/database.db')
    
    if not db_path.exists():
        print(f"\n❌ Database not found: {db_path}")
        print("   Please ensure the database exists before creating a backup.")
        return 1
    
    # Get database size
    db_size = db_path.stat().st_size / (1024 * 1024)  # MB
    print(f"\n📊 Database: {db_path}")
    print(f"📊 Size: {db_size:.2f} MB")
    
    # Create backup manager
    backup_manager = DatabaseBackupManager(str(db_path), 'backups')
    
    # Show current backup stats
    stats = backup_manager.get_backup_stats()
    print(f"\n📋 Existing Backups:")
    print(f"   Total: {stats['total_backups']}")
    print(f"   Total size: {stats['total_size_mb']:.2f} MB")
    
    if stats['newest_backup']:
        print(f"   Last backup: {stats['newest_backup']}")
    
    # Create backup
    print(f"\n🔄 Creating backup...")
    print(f"   Compressing: Yes")
    print(f"   Location: backups/")
    
    backup_path = backup_manager.create_backup(compress=True)
    
    if backup_path:
        backup_size = backup_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Backup created successfully!")
        print(f"   File: {backup_path.name}")
        print(f"   Size: {backup_size:.2f} MB")
        print(f"   Path: {backup_path}")
        
        # Cleanup old backups
        print(f"\n🧹 Cleaning up old backups...")
        backup_manager.cleanup_old_backups(
            keep_daily=7,      # Keep 7 days
            keep_weekly=4,     # Keep 4 weeks
            keep_monthly=6     # Keep 6 months
        )
        
        # Show updated stats
        stats = backup_manager.get_backup_stats()
        print(f"\n📊 Updated Stats:")
        print(f"   Total backups: {stats['total_backups']}")
        print(f"   Total size: {stats['total_size_mb']:.2f} MB")
        
        # List recent backups
        print(f"\n📋 Recent Backups:")
        backups = backup_manager.list_backups()
        for backup in backups[:5]:
            print(f"   • {backup['name']}")
            print(f"     {backup['size_mb']:.2f} MB | {backup['age_days']} days old")
        
        if len(backups) > 5:
            print(f"   ... and {len(backups) - 5} more")
        
        print(f"\n✅ Backup completed successfully!")
        print("=" * 70)
        return 0
    else:
        print(f"\n❌ Backup failed!")
        print("   Check logs for details.")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    exit(main())
