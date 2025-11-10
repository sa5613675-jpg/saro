"""
SMS Template Management Routes
Manage SMS templates for various notifications
"""
from flask import Blueprint, request, jsonify, session
from models import db, Settings, User
from utils.auth import login_required, require_role, get_current_user
from utils.response import success_response, error_response
from utils.sms_templates import get_sms_template, get_default_template, save_sms_template, get_all_saved_templates
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

sms_templates_bp = Blueprint('sms_templates', __name__)

@sms_templates_bp.route('', methods=['GET'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def get_templates():
    """Get all SMS templates"""
    try:
        # Get all saved templates from database
        saved_templates = get_all_saved_templates()
        
        # Template definitions
        template_definitions = [
            {
                'id': 'exam_result',
                'name': 'Exam Result',
                'category': 'exam',
                'description': 'Template for exam result notifications',
                'variables': ['student_name', 'subject', 'marks', 'total', 'grade', 'date'],
                'default': get_default_template('exam_result')
            },
            {
                'id': 'attendance_present',
                'name': 'Attendance Present',
                'category': 'attendance',
                'description': 'Template for present attendance notifications',
                'variables': ['student_name', 'batch_name', 'date'],
                'default': get_default_template('attendance_present')
            },
            {
                'id': 'attendance_absent',
                'name': 'Attendance Absent',
                'category': 'attendance',
                'description': 'Template for absent attendance notifications',
                'variables': ['student_name', 'batch_name', 'date'],
                'default': get_default_template('attendance_absent')
            },
            {
                'id': 'exam_good',
                'name': 'Exam Good Performance',
                'category': 'exam',
                'description': 'Template for good exam results',
                'variables': ['student_name', 'subject', 'marks', 'total', 'grade'],
                'default': get_default_template('exam_result')
            },
            {
                'id': 'exam_poor',
                'name': 'Exam Needs Improvement',
                'category': 'exam',
                'description': 'Template for results needing improvement',
                'variables': ['student_name', 'subject', 'marks', 'total', 'grade'],
                'default': get_default_template('exam_result')
            },
            {
                'id': 'fee_reminder',
                'name': 'Fee Reminder',
                'category': 'fee',
                'description': 'Template for fee reminder notifications',
                'variables': ['student_name', 'amount', 'due_date'],
                'default': get_default_template('fee_reminder')
            }
        ]
        
        # Build response with saved or default messages
        templates = []
        for template_def in template_definitions:
            template_id = template_def['id']
            # Use saved template from database if available, otherwise use default
            message = saved_templates.get(template_id, template_def['default'])
            
            templates.append({
                'id': template_id,
                'name': template_def['name'],
                'category': template_def['category'],
                'description': template_def['description'],
                'variables': template_def['variables'],
                'message': message,
                'is_saved': template_id in saved_templates
            })
        
        return jsonify(templates), 200
        
    except Exception as e:
        logger.error(f"Error getting SMS templates: {e}")
        return error_response('Failed to retrieve templates', 500)

@sms_templates_bp.route('/<template_type>', methods=['POST', 'PUT'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def update_template(template_type):
    """Update SMS template and save to database permanently"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return error_response('Template message is required', 400)
        
        message = data['message'].strip()
        if not message:
            return error_response('Template message cannot be empty', 400)
        
        current_user = get_current_user()
        
        # Save to database permanently (global for all users)
        # Note: Character limit validation is done on frontend
        success = save_sms_template(template_type, message, current_user.id)
        
        if success:
            # Clear session template if exists (database takes priority)
            if 'custom_templates' in session and template_type in session['custom_templates']:
                del session['custom_templates'][template_type]
            
            logger.info(f"Template '{template_type}' saved globally by user {current_user.id}")
            
            return success_response('Template saved successfully for all users', {
                'template_type': template_type,
                'message': message
            })
        else:
            return error_response('Failed to save template to database', 500)
        
    except Exception as e:
        logger.error(f"Error updating SMS template: {e}")
        return error_response('Failed to update template', 500)

@sms_templates_bp.route('/<template_type>/save', methods=['POST'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def save_template(template_type):
    """Save SMS template to database permanently"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return error_response('Template message is required', 400)
        
        message = data['message'].strip()
        if not message:
            return error_response('Template message cannot be empty', 400)
        
        current_user = get_current_user()
        
        # Use centralized utility to save template
        success = save_sms_template(template_type, message, current_user.id)
        
        if success:
            # Also clear session template if exists
            if 'custom_templates' in session and template_type in session['custom_templates']:
                del session['custom_templates'][template_type]
            
            return success_response('Template saved successfully', {
                'template_type': template_type,
                'message': message
            })
        else:
            return error_response('Failed to save template to database', 500)
        
    except Exception as e:
        logger.error(f"Error saving SMS template: {e}")
        return error_response('Failed to save template', 500)

@sms_templates_bp.route('/<template_type>/reset', methods=['POST'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def reset_template(template_type):
    """Reset SMS template to default"""
    try:
        # Remove from session
        if 'custom_templates' in session and template_type in session['custom_templates']:
            del session['custom_templates'][template_type]
        
        # Get default template
        default_message = get_default_template(template_type)
        
        return success_response('Template reset to default', {
            'template_type': template_type,
            'message': default_message
        })
        
    except Exception as e:
        logger.error(f"Error resetting SMS template: {e}")
        return error_response('Failed to reset template', 500)

@sms_templates_bp.route('/preview', methods=['POST'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def preview_template():
    """Preview SMS template with sample data"""
    try:
        data = request.get_json()
        
        if not data or 'template' not in data or 'template_type' not in data:
            return error_response('Template and template type are required', 400)
        
        template = data['template']
        template_type = data['template_type']
        
        # Sample data for different template types
        sample_data = {
            'exam_result': {
                'student_name': 'আহমেদ আলী',
                'subject': 'গণিত',
                'marks': 85,
                'total': 100,
                'grade': 'A',
                'percentage': 85.0,
                'date': datetime.now().strftime('%d/%m/%Y')
            },
            'attendance': {
                'student_name': 'ফাতিমা খান',
                'status': 'উপস্থিত',
                'date': datetime.now().strftime('%d/%m/%Y')
            },
            'fee_reminder': {
                'student_name': 'রহিম উদ্দিন',
                'amount': 2500,
                'due_date': '৩১/১২/২০২৪'
            }
        }
        
        try:
            # Generate preview message
            preview_data = sample_data.get(template_type, {})
            preview_message = template.format(**preview_data)
            
            return success_response('Preview generated successfully', {
                'preview': preview_message,
                'length': len(preview_message),
                'sms_count': 1 if len(preview_message) <= 160 else 2,
                'sample_data': preview_data
            })
            
        except KeyError as e:
            return error_response(f'Invalid template variable: {str(e)}', 400)
        except Exception as e:
            return error_response(f'Template format error: {str(e)}', 400)
        
    except Exception as e:
        logger.error(f"Error previewing SMS template: {e}")
        return error_response('Failed to generate preview', 500)
