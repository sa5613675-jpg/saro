#!/usr/bin/env python3
"""
Database Backup System for SQLite
Automatically creates backups with rotation and cleanup
"""
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging
import gzip

logger = logging.getLogger(__name__)


class DatabaseBackupManager:
    """Manages SQLite database backups with rotation"""
    
    def __init__(self, db_path, backup_dir='backups'):
        """
        Initialize backup manager
        
        Args:
            db_path: Path to SQLite database file
            backup_dir: Directory to store backups
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, compress=True):
        """
        Create a database backup
        
        Args:
            compress: Whether to compress the backup with gzip
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            if not self.db_path.exists():
                logger.error(f"Database file not found: {self.db_path}")
                return None
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"database_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_name
            
            # Create backup using SQLite backup API (safer than file copy)
            logger.info(f"Creating backup: {backup_path}")
            
            # Connect to source and destination databases
            source_conn = sqlite3.connect(str(self.db_path))
            dest_conn = sqlite3.connect(str(backup_path))
            
            # Perform backup
            with dest_conn:
                source_conn.backup(dest_conn)
            
            source_conn.close()
            dest_conn.close()
            
            # Get backup size
            backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"Backup created successfully: {backup_size:.2f} MB")
            
            # Compress if requested
            if compress:
                compressed_path = self._compress_backup(backup_path)
                if compressed_path:
                    backup_path.unlink()  # Remove uncompressed version
                    backup_path = compressed_path
                    compressed_size = backup_path.stat().st_size / (1024 * 1024)
                    logger.info(f"Backup compressed: {compressed_size:.2f} MB")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def _compress_backup(self, backup_path):
        """Compress backup file with gzip"""
        try:
            compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return compressed_path
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return None
    
    def cleanup_old_backups(self, keep_daily=7, keep_weekly=4, keep_monthly=6):
        """
        Clean up old backups based on retention policy
        
        Args:
            keep_daily: Number of daily backups to keep (default: 7 days)
            keep_weekly: Number of weekly backups to keep (default: 4 weeks)
            keep_monthly: Number of monthly backups to keep (default: 6 months)
        """
        try:
            # Get all backup files
            backups = sorted(
                self.backup_dir.glob('database_backup_*.db*'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if not backups:
                logger.info("No backups found to clean up")
                return
            
            now = datetime.now()
            kept_backups = []
            daily_count = 0
            weekly_count = 0
            monthly_count = 0
            
            for backup in backups:
                # Get backup age
                backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
                age_days = (now - backup_time).days
                
                keep = False
                reason = ""
                
                # Keep daily backups
                if age_days < keep_daily and daily_count < keep_daily:
                    keep = True
                    daily_count += 1
                    reason = f"daily ({age_days} days old)"
                
                # Keep weekly backups (one per week)
                elif age_days < keep_weekly * 7 and weekly_count < keep_weekly:
                    # Check if this is the newest backup for its week
                    week_num = backup_time.isocalendar()[1]
                    if not any(
                        datetime.fromtimestamp(b.stat().st_mtime).isocalendar()[1] == week_num
                        for b in kept_backups
                    ):
                        keep = True
                        weekly_count += 1
                        reason = f"weekly ({age_days} days old)"
                
                # Keep monthly backups (one per month)
                elif age_days < keep_monthly * 30 and monthly_count < keep_monthly:
                    # Check if this is the newest backup for its month
                    month = backup_time.month
                    if not any(
                        datetime.fromtimestamp(b.stat().st_mtime).month == month
                        for b in kept_backups
                    ):
                        keep = True
                        monthly_count += 1
                        reason = f"monthly ({age_days} days old)"
                
                if keep:
                    kept_backups.append(backup)
                    logger.info(f"Keeping {backup.name}: {reason}")
                else:
                    logger.info(f"Deleting old backup: {backup.name} ({age_days} days old)")
                    backup.unlink()
            
            logger.info(
                f"Cleanup complete. Kept {len(kept_backups)} backups "
                f"({daily_count} daily, {weekly_count} weekly, {monthly_count} monthly)"
            )
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def restore_backup(self, backup_path, restore_to=None):
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            restore_to: Path to restore to (default: original db_path)
            
        Returns:
            bool: True if successful
        """
        try:
            backup_path = Path(backup_path)
            restore_to = Path(restore_to) if restore_to else self.db_path
            
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Decompress if needed
            temp_backup = backup_path
            if backup_path.suffix == '.gz':
                temp_backup = backup_path.with_suffix('')
                logger.info(f"Decompressing backup: {backup_path}")
                
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_backup, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            # Backup current database before restoring
            if restore_to.exists():
                current_backup = restore_to.with_suffix('.db.before_restore')
                shutil.copy2(restore_to, current_backup)
                logger.info(f"Current database backed up to: {current_backup}")
            
            # Restore backup
            logger.info(f"Restoring backup to: {restore_to}")
            shutil.copy2(temp_backup, restore_to)
            
            # Clean up temporary file if we decompressed
            if temp_backup != backup_path:
                temp_backup.unlink()
            
            logger.info("Restore completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def list_backups(self):
        """List all available backups with details"""
        backups = sorted(
            self.backup_dir.glob('database_backup_*.db*'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        backup_info = []
        for backup in backups:
            stat = backup.stat()
            backup_info.append({
                'name': backup.name,
                'path': str(backup),
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_mtime),
                'age_days': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
            })
        
        return backup_info
    
    def get_backup_stats(self):
        """Get backup statistics"""
        backups = list(self.backup_dir.glob('database_backup_*.db*'))
        
        if not backups:
            return {
                'total_backups': 0,
                'total_size_mb': 0,
                'oldest_backup': None,
                'newest_backup': None
            }
        
        total_size = sum(b.stat().st_size for b in backups)
        oldest = min(backups, key=lambda p: p.stat().st_mtime)
        newest = max(backups, key=lambda p: p.stat().st_mtime)
        
        return {
            'total_backups': len(backups),
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_backup': datetime.fromtimestamp(oldest.stat().st_mtime),
            'newest_backup': datetime.fromtimestamp(newest.stat().st_mtime)
        }


def create_backup(db_path='instance/database.db', backup_dir='backups'):
    """Convenience function to create a backup"""
    manager = DatabaseBackupManager(db_path, backup_dir)
    backup_path = manager.create_backup(compress=True)
    
    if backup_path:
        # Clean up old backups
        manager.cleanup_old_backups(
            keep_daily=7,      # Keep 7 days of daily backups
            keep_weekly=4,     # Keep 4 weeks of weekly backups
            keep_monthly=6     # Keep 6 months of monthly backups
        )
        return backup_path
    
    return None


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create backup
    print("=" * 70)
    print("DATABASE BACKUP UTILITY")
    print("=" * 70)
    
    db_path = 'instance/database.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        exit(1)
    
    manager = DatabaseBackupManager(db_path)
    
    # Show current stats
    stats = manager.get_backup_stats()
    print(f"\n📊 Current Backup Stats:")
    print(f"   Total backups: {stats['total_backups']}")
    print(f"   Total size: {stats['total_size_mb']:.2f} MB")
    if stats['newest_backup']:
        print(f"   Newest backup: {stats['newest_backup']}")
    
    # Create new backup
    print(f"\n🔄 Creating new backup...")
    backup_path = manager.create_backup(compress=True)
    
    if backup_path:
        print(f"✅ Backup created: {backup_path}")
        
        # Cleanup old backups
        print(f"\n🧹 Cleaning up old backups...")
        manager.cleanup_old_backups(
            keep_daily=7,
            keep_weekly=4,
            keep_monthly=6
        )
        
        # List all backups
        print(f"\n📋 Available Backups:")
        backups = manager.list_backups()
        for backup in backups[:10]:  # Show first 10
            print(f"   • {backup['name']}")
            print(f"     Size: {backup['size_mb']:.2f} MB | Age: {backup['age_days']} days")
        
        if len(backups) > 10:
            print(f"   ... and {len(backups) - 10} more")
    else:
        print(f"❌ Backup failed!")
    
    print("=" * 70)
