#!/bin/bash
#
# Setup Automatic Weekly Database Backups (Cron Job)
# This script sets up a cron job to run backups automatically
#

echo "======================================================================"
echo "  AUTOMATIC DATABASE BACKUP SETUP"
echo "======================================================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create backup script
cat > /tmp/backup_cron.sh << 'EOFSCRIPT'
#!/bin/bash
# Auto-generated backup script
# Runs database backup and logs output

# Change to application directory
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

# Run backup and log output
echo "========================================" >> logs/backup_cron.log
echo "Backup started: $(date)" >> logs/backup_cron.log
python3 backup_database.py >> logs/backup_cron.log 2>&1
echo "Backup finished: $(date)" >> logs/backup_cron.log
echo "========================================" >> logs/backup_cron.log
EOFSCRIPT

# Move backup script to application directory
mv /tmp/backup_cron.sh "$SCRIPT_DIR/backup_cron.sh"
chmod +x "$SCRIPT_DIR/backup_cron.sh"

echo "✅ Backup script created: $SCRIPT_DIR/backup_cron.sh"
echo ""

# Create cron job entry
CRON_JOB="0 2 * * 0 cd $SCRIPT_DIR && ./backup_cron.sh"

echo "📅 Cron job to be added:"
echo "   $CRON_JOB"
echo ""
echo "   This will run:"
echo "   - Every Sunday at 2:00 AM"
echo "   - Logs saved to: logs/backup_cron.log"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "backup_cron.sh"; then
    echo "⚠️  Cron job already exists!"
    echo ""
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
    # Remove existing cron job
    crontab -l 2>/dev/null | grep -v "backup_cron.sh" | crontab -
fi

# Add cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✅ Cron job added successfully!"
echo ""
echo "======================================================================"
echo "  SETUP COMPLETE"
echo "======================================================================"
echo ""
echo "Backup schedule:"
echo "  - Automatic: Every Sunday at 2:00 AM"
echo "  - Logs: $SCRIPT_DIR/logs/backup_cron.log"
echo ""
echo "Manual commands:"
echo "  - Create backup now:    python3 backup_database.py"
echo "  - Restore from backup:  python3 restore_database.py"
echo "  - View cron jobs:       crontab -l"
echo "  - Remove cron job:      crontab -e (then delete the line)"
echo ""
echo "Backup retention policy:"
echo "  - Daily backups: 7 days"
echo "  - Weekly backups: 4 weeks"
echo "  - Monthly backups: 6 months"
echo ""
echo "======================================================================"
