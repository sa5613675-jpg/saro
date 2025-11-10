# SQLite Production Database with Automatic Backups

## ✅ IMPLEMENTED FEATURES

### 1. SQLite for Production
- **Database**: SQLite (same for development and production)
- **Location**: `instance/database.db`
- **Advantages**:
  - No separate database server needed
  - Easy deployment
  - Zero configuration
  - Perfect for small to medium applications
  - Built-in with Python

### 2. Automatic Weekly Backups
- **Schedule**: Every Sunday at 2:00 AM
- **Daily Backup**: Every day at 3:00 AM (optional)
- **Compression**: Automatic gzip compression
- **Retention Policy**:
  - Daily backups: 7 days
  - Weekly backups: 4 weeks
  - Monthly backups: 6 months

---

## 📂 Backup System Components

### Files Created:

1. **`utils/database_backup.py`** - Core backup functionality
   - `DatabaseBackupManager` class
   - Create, restore, list backups
   - Automatic cleanup based on retention policy

2. **`utils/backup_scheduler.py`** - Automatic scheduling
   - Weekly backups (Sunday 2:00 AM)
   - Daily backups (3:00 AM)
   - Integrated with Flask app

3. **`backup_database.py`** - Manual backup script
   - Run immediate backup
   - View backup stats
   - List existing backups

4. **`restore_database.py`** - Restore utility
   - Interactive backup selection
   - Safe restoration with pre-restore backup

5. **`setup_backup_cron.sh`** - Cron job setup
   - Automated weekly backups via cron
   - Logging to `logs/backup_cron.log`

---

## 🚀 Usage

### Manual Backup
```bash
# Create an immediate backup
python3 backup_database.py
```

**Output**:
```
✅ Backup created successfully!
   File: database_backup_20251110_025851.db.gz
   Size: 0.15 MB
   Path: backups/database_backup_20251110_025851.db.gz
```

### Restore from Backup
```bash
# Interactive restore
python3 restore_database.py
```

**Features**:
- Lists all available backups
- Interactive selection
- Creates safety backup before restoring
- Automatic decompression

### Setup Automatic Backups (Cron)
```bash
# Setup weekly cron job
bash setup_backup_cron.sh
```

**Result**:
- Backup runs every Sunday at 2:00 AM
- Logs saved to `logs/backup_cron.log`

---

## 📊 Backup Retention Policy

| Type | Retention | Example |
|------|-----------|---------|
| **Daily** | 7 days | Mon, Tue, Wed, Thu, Fri, Sat, Sun |
| **Weekly** | 4 weeks | Week 1, Week 2, Week 3, Week 4 |
| **Monthly** | 6 months | Jan, Feb, Mar, Apr, May, Jun |

**Auto-cleanup**: Old backups are automatically deleted when creating new ones.

---

## 🔧 Configuration

### Database Path (config.py)
```python
# Production
DATABASE_PATH = 'instance/database.db'
BACKUP_DIR = 'backups/'

# Can be overridden with environment variables
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'instance/database.db')
BACKUP_DIR = os.environ.get('BACKUP_DIR', 'backups')
```

### Production Settings (config.py)
```python
class ProductionConfig(Config):
    DEBUG = False
    
    # SQLite with optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'timeout': 30,  # 30 second timeout
            'check_same_thread': False  # Multi-threading support
        },
        'pool_pre_ping': True,  # Verify connections
        'pool_recycle': 300  # Recycle every 5 minutes
    }
```

---

## 📋 Backup File Naming

Format: `database_backup_YYYYMMDD_HHMMSS.db.gz`

Examples:
```
database_backup_20251110_020000.db.gz  (Sunday 2AM - weekly)
database_backup_20251111_030000.db.gz  (Monday 3AM - daily)
database_backup_20251112_030000.db.gz  (Tuesday 3AM - daily)
```

---

## 🔍 Monitoring Backups

### List All Backups
```python
from utils.database_backup import DatabaseBackupManager

manager = DatabaseBackupManager('instance/database.db', 'backups')

# Get stats
stats = manager.get_backup_stats()
print(f"Total backups: {stats['total_backups']}")
print(f"Total size: {stats['total_size_mb']:.2f} MB")
print(f"Latest backup: {stats['newest_backup']}")

# List all backups
backups = manager.list_backups()
for backup in backups:
    print(f"{backup['name']} - {backup['size_mb']:.2f} MB - {backup['age_days']} days old")
```

### Check Backup Logs
```bash
# View cron backup logs
tail -f logs/backup_cron.log

# View latest backups
ls -lh backups/
```

---

## 🛠️ Maintenance Commands

### View Cron Jobs
```bash
crontab -l
```

### Edit Cron Jobs
```bash
crontab -e
```

### Remove Cron Jobs
```bash
crontab -r
```

### Manual Cleanup
```python
from utils.database_backup import DatabaseBackupManager

manager = DatabaseBackupManager('instance/database.db', 'backups')

# Custom retention
manager.cleanup_old_backups(
    keep_daily=14,     # Keep 14 days
    keep_weekly=8,     # Keep 8 weeks
    keep_monthly=12    # Keep 12 months
)
```

---

## 🚨 Disaster Recovery

### Complete Restore Process

1. **Stop the application**
```bash
# Stop Flask app
pkill -f "python.*app.py"
```

2. **Restore from backup**
```bash
python3 restore_database.py
# Select backup from list
# Confirm restoration
```

3. **Restart application**
```bash
python3 app.py
# or
gunicorn app:app
```

### Alternative Manual Restore
```bash
# Decompress backup
gunzip backups/database_backup_20251110_020000.db.gz

# Backup current database
cp instance/database.db instance/database.db.backup

# Restore
cp backups/database_backup_20251110_020000.db instance/database.db
```

---

## 📈 Production Deployment

### Environment Variables
```bash
# .env file
FLASK_ENV=production
DATABASE_PATH=/path/to/database.db
BACKUP_DIR=/path/to/backups
SECRET_KEY=your-production-secret-key
```

### Running in Production
```bash
# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Automatic backups run in background via:
# 1. Cron job (setup_backup_cron.sh)
# OR
# 2. Application scheduler (integrated in app.py)
```

---

## ✅ Advantages of This System

### SQLite Benefits:
✅ **Simple**: No separate database server  
✅ **Fast**: Direct file access  
✅ **Reliable**: ACID compliant  
✅ **Portable**: Single file database  
✅ **Zero Config**: Works out of the box  

### Backup System Benefits:
✅ **Automatic**: Weekly scheduled backups  
✅ **Compressed**: Saves storage space (gzip)  
✅ **Retention**: Intelligent cleanup policy  
✅ **Safe**: Creates backup before restore  
✅ **Logged**: All operations logged  
✅ **Manual**: Run backups anytime  

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| **Manual Backup** | `python3 backup_database.py` |
| **Restore** | `python3 restore_database.py` |
| **Setup Cron** | `bash setup_backup_cron.sh` |
| **View Logs** | `tail -f logs/backup_cron.log` |
| **List Backups** | `ls -lh backups/` |
| **View Cron Jobs** | `crontab -l` |

---

## 🎯 System Ready!

✅ SQLite configured for production  
✅ Automatic weekly backups enabled  
✅ Manual backup/restore scripts ready  
✅ Retention policy configured  
✅ Logging enabled  
✅ Cron job setup available  

**Your database is now protected with automatic backups! 🎉**
