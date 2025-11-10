"""
SMS Template Utilities
Centralized SMS template management with database persistence
"""
import logging
from flask import session

logger = logging.getLogger(__name__)


def get_sms_template(template_type):
    """
    Get SMS template with priority order:
    1. Database saved template (permanent, cross-session)
    2. Session template (temporary override)
    3. Default template (fallback)
    
    This ensures saved templates work across different IPs and browser sessions.
    """
    try:
        from models import Settings
        
        # PRIORITY 1: Try to get template from Settings table (permanent storage)
        template_key = f"sms_template_{template_type}"
        template_setting = Settings.query.filter_by(key=template_key).first()
        
        if template_setting and template_setting.value:
            saved_message = template_setting.value.get('message')
            if saved_message:
                logger.debug(f"Using database template for {template_type}")
                return saved_message
        
        # PRIORITY 2: Fall back to session template (temporary override)
        custom_templates = session.get('custom_templates', {})
        custom_template = custom_templates.get(template_type)
        
        if custom_template:
            logger.debug(f"Using session template for {template_type}")
            return custom_template
        
        # PRIORITY 3: Return default template
        logger.debug(f"Using default template for {template_type}")
        return get_default_template(template_type)
        
    except Exception as e:
        logger.warning(f"Error getting SMS template: {e}")
        return get_default_template(template_type)


def get_default_template(template_type):
    """Get default SMS templates"""
    templates = {
        'exam_result': "Dear Parent, {student_name} scored {marks}/{total} marks in {subject} exam on {date}. Grade: {grade}",
        'exam_good': "Dear Parent, {student_name} scored {marks}/{total} marks in {subject}. Grade: {grade}. Excellent performance!",
        'exam_poor': "Dear Parent, {student_name} scored {marks}/{total} marks in {subject}. Grade: {grade}. Needs improvement.",
        'attendance': "Dear Parent, {student_name} was {status} in class on {date}.",
        'attendance_present': "Dear Parent, {student_name} was PRESENT today in {batch_name} on {date}. Keep up the good work!",
        'attendance_absent': "Dear Parent, {student_name} was ABSENT today in {batch_name} on {date}. Please ensure regular attendance.",
        'fee_reminder': "Dear Parent, monthly fee for {student_name} is due. Amount: {amount} BDT. Please pay by {due_date}.",
        'general': "Dear Parent, this is an update regarding {student_name}."
    }
    return templates.get(template_type, templates['general'])


def save_sms_template(template_type, message, user_id):
    """
    Save SMS template to database permanently
    
    Args:
        template_type: Type of template (exam_result, attendance, etc.)
        message: Template message content
        user_id: ID of user saving the template
    
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        from models import Settings, db
        from datetime import datetime
        
        template_key = f"sms_template_{template_type}"
        
        # Check if template exists
        template_setting = Settings.query.filter_by(key=template_key).first()
        
        if template_setting:
            # Update existing template
            template_setting.value = {'message': message}
            template_setting.updated_by = user_id
            template_setting.updated_at = datetime.utcnow()
            logger.info(f"Updated SMS template: {template_type}")
        else:
            # Create new template
            template_setting = Settings(
                key=template_key,
                value={'message': message},
                description=f"SMS template for {template_type}",
                category="sms_templates",
                updated_by=user_id
            )
            db.session.add(template_setting)
            logger.info(f"Created SMS template: {template_type}")
        
        db.session.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error saving SMS template: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return False


def get_all_saved_templates():
    """
    Get all saved SMS templates from database
    
    Returns:
        dict: Dictionary of template_type -> message
    """
    try:
        from models import Settings
        
        saved_templates = {}
        db_templates = Settings.query.filter(
            Settings.key.like('sms_template_%')
        ).all()
        
        for db_template in db_templates:
            template_type = db_template.key.replace('sms_template_', '')
            if db_template.value:
                message = db_template.value.get('message')
                if message:
                    saved_templates[template_type] = message
        
        return saved_templates
        
    except Exception as e:
        logger.error(f"Error getting saved templates: {e}")
        return {}
