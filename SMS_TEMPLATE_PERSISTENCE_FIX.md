# SMS Template Persistence Fix

## Problem
SMS templates were only saved for a specific IP address or browser session. When accessing the system from a different IP or browser, the saved templates would not appear, and the system would fall back to default templates.

## Root Cause
The template retrieval logic had the wrong priority order:
1. ❌ Session templates (browser/IP-specific) - checked FIRST
2. ❌ Database templates (permanent) - checked SECOND
3. ❌ Default templates (fallback) - checked LAST

This meant that even if a template was saved to the database, it would be overridden by session data (or lack thereof) from a different browser/IP.

## Solution
Reversed the priority order to ensure database-saved templates are used first:
1. ✅ **Database saved template** (permanent, cross-session) - checked FIRST
2. ✅ **Session template** (temporary override) - checked SECOND
3. ✅ **Default template** (fallback) - checked LAST

## Changes Made

### 1. Created Centralized Utility (`utils/sms_templates.py`)
A new utility module provides consistent template management:
- `get_sms_template(template_type)` - Get template with correct priority order
- `save_sms_template(template_type, message, user_id)` - Save template to database
- `get_default_template(template_type)` - Get default template
- `get_all_saved_templates()` - Get all saved templates from database

### 2. Updated Template Routes (`routes/sms_templates.py`)
- Now uses centralized utility functions
- Database templates have priority when displaying current template
- Save function clears session template after saving to database
- Added support for `attendance_present` and `attendance_absent` templates

### 3. Updated Monthly Exams (`routes/monthly_exams.py`)
- Replaced inline template logic with centralized utility
- Database templates are now used for exam result SMS

### 4. Updated Attendance (`routes/attendance.py`)
- Replaced inline template logic with centralized utility
- Database templates are now used for attendance SMS (present/absent)

## Template Types Supported
1. `exam_result` - Exam result notifications
2. `attendance` - General attendance notifications
3. `attendance_present` - Present attendance notifications
4. `attendance_absent` - Absent attendance notifications
5. `fee_reminder` - Fee reminder notifications

## How It Works

### Saving Templates
1. User edits template in the UI
2. User clicks "Save" button
3. Template is saved to `settings` table with key `sms_template_{type}`
4. Session template is cleared (if exists)
5. Template now persists across all IPs and browser sessions

### Retrieving Templates
1. System checks database for saved template (permanent)
2. If not found, checks session for temporary override
3. If not found, uses default template

### Database Storage
Templates are stored in the `settings` table:
- **Key**: `sms_template_{template_type}` (e.g., `sms_template_exam_result`)
- **Value**: `{'message': 'template content...'}`
- **Category**: `sms_templates`
- **Updated by**: User ID who saved the template
- **Updated at**: Timestamp of last update

## Testing
Run the test script to verify the fix:
```bash
python test_sms_template_persistence.py
```

The test verifies:
1. ✅ Templates save to database successfully
2. ✅ Templates persist across different sessions/IPs
3. ✅ Database templates have priority over session templates
4. ✅ Multiple template types work correctly

## Benefits
1. **Cross-session persistence** - Templates work from any IP/browser
2. **Database-backed** - Templates stored in permanent database storage
3. **Centralized logic** - Single source of truth for template management
4. **Backward compatible** - Session templates still work as temporary overrides
5. **Consistent behavior** - All modules use the same template retrieval logic

## Migration
No database migration required - the `settings` table already exists and supports the required structure.

## Files Modified
- ✅ `utils/sms_templates.py` (NEW)
- ✅ `routes/sms_templates.py`
- ✅ `routes/monthly_exams.py`
- ✅ `routes/attendance.py`
- ✅ `test_sms_template_persistence.py` (NEW)
