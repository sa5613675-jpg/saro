#!/usr/bin/env python3
"""
Automatic Database Backup Scheduler
Runs weekly backups using APScheduler
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from utils.database_backup import DatabaseBackupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class BackupScheduler:
    """Manages scheduled database backups"""
    
    def __init__(self, db_path='instance/database.db', backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.scheduler = BackgroundScheduler()
        self.backup_manager = DatabaseBackupManager(db_path, backup_dir)
        
        # Ensure logs directory exists
        Path('logs').mkdir(exist_ok=True)
    
    def backup_job(self):
        """Execute backup job"""
        try:
            logger.info("=" * 70)
            logger.info("SCHEDULED BACKUP STARTING")
            logger.info("=" * 70)
            
            # Create backup
            backup_path = self.backup_manager.create_backup(compress=True)
            
            if backup_path:
                logger.info(f"✅ Backup created successfully: {backup_path}")
                
                # Cleanup old backups
                logger.info("Cleaning up old backups...")
                self.backup_manager.cleanup_old_backups(
                    keep_daily=7,      # Keep 7 days
                    keep_weekly=4,     # Keep 4 weeks
                    keep_monthly=6     # Keep 6 months
                )
                
                # Get stats
                stats = self.backup_manager.get_backup_stats()
                logger.info(f"📊 Total backups: {stats['total_backups']}")
                logger.info(f"📊 Total size: {stats['total_size_mb']:.2f} MB")
                
                logger.info("✅ SCHEDULED BACKUP COMPLETED SUCCESSFULLY")
            else:
                logger.error("❌ SCHEDULED BACKUP FAILED")
            
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Backup job failed: {e}", exc_info=True)
    
    def start(self):
        """Start the backup scheduler"""
        try:
            # Schedule weekly backup (every Sunday at 2:00 AM)
            self.scheduler.add_job(
                self.backup_job,
                trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
                id='weekly_backup',
                name='Weekly Database Backup',
                replace_existing=True
            )
            
            # Also schedule daily backup at 3:00 AM (optional)
            self.scheduler.add_job(
                self.backup_job,
                trigger=CronTrigger(hour=3, minute=0),
                id='daily_backup',
                name='Daily Database Backup',
                replace_existing=True
            )
            
            self.scheduler.start()
            
            logger.info("🚀 Backup scheduler started")
            logger.info("📅 Weekly backup: Every Sunday at 2:00 AM")
            logger.info("📅 Daily backup: Every day at 3:00 AM")
            
            # Log next run times
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                logger.info(f"   {job.name}: Next run at {job.next_run_time}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the backup scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Backup scheduler stopped")
    
    def run_manual_backup(self):
        """Run backup manually"""
        logger.info("Running manual backup...")
        self.backup_job()


def init_backup_scheduler(app):
    """Initialize backup scheduler with Flask app"""
    try:
        # Get database path from app config
        db_path = app.config.get('DATABASE_PATH', 'instance/database.db')
        backup_dir = app.config.get('BACKUP_DIR', 'backups')
        
        scheduler = BackupScheduler(db_path, backup_dir)
        scheduler.start()
        
        # Store scheduler in app for later access
        app.backup_scheduler = scheduler
        
        logger.info("✅ Backup scheduler initialized successfully")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"Failed to initialize backup scheduler: {e}")
        return None


if __name__ == '__main__':
    # Run as standalone script
    print("Starting backup scheduler...")
    
    scheduler = BackupScheduler()
    
    # Run immediate backup
    print("Running immediate backup...")
    scheduler.run_manual_backup()
    
    # Start scheduler
    scheduler.start()
    
    print("\nScheduler is running. Press Ctrl+C to stop.")
    print("Scheduled times:")
    print("  - Weekly: Every Sunday at 2:00 AM")
    print("  - Daily: Every day at 3:00 AM")
    
    try:
        # Keep the script running
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down scheduler...")
        scheduler.stop()
        print("Scheduler stopped.")
