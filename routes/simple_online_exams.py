"""
Simple Online Exams Routes - Teacher & Student Side
Routes for creating and taking simple MCQ exams
"""
from flask import Blueprint, request, jsonify, session
from models import db, OnlineExam, ExamQuestion, StudentExamAttempt, Batch, User
from utils.auth import login_required, get_current_user
from datetime import datetime, timedelta
import json

simple_exams_bp = Blueprint('simple_exams', __name__)

# ============= TEACHER ROUTES =============

@simple_exams_bp.route('/api/simple-exams', methods=['GET'])
@login_required
def get_exams():
    """Get all exams created by current teacher"""
    if get_current_user().role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    exams = OnlineExam.query.filter_by(created_by=get_current_user().id).order_by(OnlineExam.created_at.desc()).all()
    return jsonify({
        'exams': [exam.to_dict() for exam in exams]
    })

@simple_exams_bp.route('/api/simple-exams/<int:exam_id>', methods=['GET'])
@login_required
def get_exam(exam_id):
    """Get a specific exam with all questions"""
    exam = OnlineExam.query.get_or_404(exam_id)
    
    # Check permission
    if get_current_user().role == 'teacher' and exam.created_by != get_current_user().id:
        return jsonify({'error': 'Access denied'}), 403
    
    exam_data = exam.to_dict()
    exam_data['questions'] = [q.to_dict(include_answer=get_current_user().role == 'teacher') for q in exam.questions]
    
    return jsonify(exam_data)

@simple_exams_bp.route('/api/simple-exams', methods=['POST'])
@login_required
def create_exam():
    """Create a new online exam with questions"""
    if get_current_user().role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    
    # Validate required fields
    required = ['batch_id', 'title', 'class_name', 'book_name', 'chapter_name', 
                'duration_minutes', 'questions']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate questions
    questions = data.get('questions', [])
    if not questions or len(questions) > 40:
        return jsonify({'error': 'Questions must be between 1 and 40'}), 400
    
    # Verify batch exists
    batch = Batch.query.get(data['batch_id'])
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    
    try:
        # Create exam
        exam = OnlineExam(
            batch_id=data['batch_id'],
            title=data['title'],
            class_name=data['class_name'],
            book_name=data['book_name'],
            chapter_name=data['chapter_name'],
            duration_minutes=data['duration_minutes'],
            total_questions=len(questions),
            pass_marks=data.get('pass_marks', 40),
            created_by=get_current_user().id,
            allow_retake=data.get('allow_retake', True)
        )
        db.session.add(exam)
        db.session.flush()  # Get exam.id
        
        # Add questions
        for i, q_data in enumerate(questions, 1):
            # Validate question format
            if not all(k in q_data for k in ['question_text', 'option_a', 'option_b', 
                                             'option_c', 'option_d', 'correct_answer']):
                db.session.rollback()
                return jsonify({'error': f'Question {i} missing required fields'}), 400
            
            # Validate correct_answer
            if q_data['correct_answer'].upper() not in ['A', 'B', 'C', 'D']:
                db.session.rollback()
                return jsonify({'error': f'Question {i} has invalid correct answer'}), 400
            
            question = ExamQuestion(
                exam_id=exam.id,
                question_number=i,
                question_text=q_data['question_text'],
                option_a=q_data['option_a'],
                option_b=q_data['option_b'],
                option_c=q_data['option_c'],
                option_d=q_data['option_d'],
                correct_answer=q_data['correct_answer'].upper(),
                explanation=q_data.get('explanation', '')
            )
            db.session.add(question)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Exam created successfully',
            'exam': exam.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@simple_exams_bp.route('/api/simple-exams/<int:exam_id>', methods=['DELETE'])
@login_required
def delete_exam(exam_id):
    """Delete an exam"""
    if get_current_user().role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    exam = OnlineExam.query.get_or_404(exam_id)
    
    # Check permission
    if exam.created_by != get_current_user().id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Questions and attempts will be cascade deleted
        db.session.delete(exam)
        db.session.commit()
        
        return jsonify({'message': 'Exam deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@simple_exams_bp.route('/api/simple-exams/<int:exam_id>/results', methods=['GET'])
@login_required
def get_exam_results(exam_id):
    """Get all student results for an exam"""
    if get_current_user().role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    exam = OnlineExam.query.get_or_404(exam_id)
    
    # Check permission
    if exam.created_by != get_current_user().id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get all submitted attempts
    attempts = StudentExamAttempt.query.filter_by(exam_id=exam_id).filter(
        StudentExamAttempt.status.in_(['submitted', 'auto_submitted'])
    ).order_by(StudentExamAttempt.submit_time.desc()).all()
    
    results = []
    for attempt in attempts:
        student = User.query.get(attempt.student_id)
        results.append({
            'attempt': attempt.to_dict(),
            'student': {
                'id': student.id,
                'name': student.name,
                'guardian_phone': student.guardian_phone
            }
        })
    
    return jsonify({
        'exam': exam.to_dict(),
        'results': results
    })

@simple_exams_bp.route('/api/batches-for-exams', methods=['GET'])
@login_required
def get_batches():
    """Get all batches for dropdown"""
    if get_current_user().role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    batches = Batch.query.filter_by(is_active=True).all()
    return jsonify({
        'batches': [{'id': b.id, 'name': b.name} for b in batches]
    })

# ============= STUDENT ROUTES =============

@simple_exams_bp.route('/api/my-exams', methods=['GET'])
@login_required
def get_my_exams():
    """Get all available exams for current student"""
    if get_current_user().role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get student's batch
    student_batches = [e.batch_id for e in get_current_user().enrollments if e.is_active]
    
    if not student_batches:
        return jsonify({'exams': []})
    
    # Get active exams for student's batches
    exams = OnlineExam.query.filter(
        OnlineExam.batch_id.in_(student_batches),
        OnlineExam.is_active == True
    ).order_by(OnlineExam.created_at.desc()).all()
    
    exam_list = []
    for exam in exams:
        # Check if student has attempted
        attempt = StudentExamAttempt.query.filter_by(
            exam_id=exam.id,
            student_id=get_current_user().id
        ).order_by(StudentExamAttempt.attempt_number.desc()).first()
        
        exam_data = exam.to_dict()
        exam_data['has_attempted'] = attempt is not None
        exam_data['can_retake'] = exam.allow_retake and attempt and attempt.status in ['submitted', 'auto_submitted']
        exam_data['last_attempt'] = attempt.to_dict() if attempt else None
        
        exam_list.append(exam_data)
    
    return jsonify({'exams': exam_list})

@simple_exams_bp.route('/api/exam/<int:exam_id>/start', methods=['POST'])
@login_required
def start_exam(exam_id):
    """Start an exam (create attempt record)"""
    if get_current_user().role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    exam = OnlineExam.query.get_or_404(exam_id)
    
    # Check if exam is active
    if not exam.is_active:
        return jsonify({'error': 'Exam is not active'}), 400
    
    # Check if student can take exam
    student_batches = [e.batch_id for e in get_current_user().enrollments if e.is_active]
    if exam.batch_id not in student_batches:
        return jsonify({'error': 'You are not enrolled in this exam batch'}), 403
    
    # Check for existing attempts
    last_attempt = StudentExamAttempt.query.filter_by(
        exam_id=exam_id,
        student_id=get_current_user().id
    ).order_by(StudentExamAttempt.attempt_number.desc()).first()
    
    # If in progress, resume
    if last_attempt and last_attempt.status == 'in_progress':
        questions = [q.to_dict(include_answer=False) for q in sorted(exam.questions, key=lambda x: x.question_number)]
        return jsonify({
            'message': 'Resuming exam',
            'attempt_id': last_attempt.id,
            'exam': exam.to_dict(),
            'questions': questions,
            'existing_answers': last_attempt.get_answers(),
            'start_time': last_attempt.start_time.isoformat()
        })
    
    # Check if can retake
    if last_attempt and last_attempt.status in ['submitted', 'auto_submitted']:
        if not exam.allow_retake:
            return jsonify({'error': 'Retakes not allowed for this exam'}), 400
    
    # Create new attempt
    attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1
    
    attempt = StudentExamAttempt(
        exam_id=exam_id,
        student_id=get_current_user().id,
        attempt_number=attempt_number,
        status='in_progress'
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Return exam with questions (without answers) - sorted by question number
    questions = [q.to_dict(include_answer=False) for q in sorted(exam.questions, key=lambda x: x.question_number)]
    
    return jsonify({
        'message': 'Exam started',
        'attempt_id': attempt.id,
        'exam': exam.to_dict(),
        'questions': questions,
        'start_time': attempt.start_time.isoformat()
    })

@simple_exams_bp.route('/api/exam/<int:exam_id>/save-answer', methods=['POST'])
@login_required
def save_answer(exam_id):
    """Save student answer (auto-save)"""
    if get_current_user().role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    question_number = data.get('question_number')
    answer = data.get('answer')  # A, B, C, or D
    
    if not question_number or not answer:
        return jsonify({'error': 'Question number and answer required'}), 400
    
    # Get active attempt
    attempt = StudentExamAttempt.query.filter_by(
        exam_id=exam_id,
        student_id=get_current_user().id,
        status='in_progress'
    ).order_by(StudentExamAttempt.start_time.desc()).first()
    
    if not attempt:
        return jsonify({'error': 'No active attempt found'}), 404
    
    # Update answers JSON
    answers = attempt.get_answers()
    answers[str(question_number)] = answer.upper()
    attempt.set_answers(answers)
    
    db.session.commit()
    
    return jsonify({'message': 'Answer saved'})

@simple_exams_bp.route('/api/exam/<int:exam_id>/submit', methods=['POST'])
@login_required
def submit_exam(exam_id):
    """Submit exam and calculate score"""
    if get_current_user().role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get active attempt
    attempt = StudentExamAttempt.query.filter_by(
        exam_id=exam_id,
        student_id=get_current_user().id,
        status='in_progress'
    ).order_by(StudentExamAttempt.start_time.desc()).first()
    
    if not attempt:
        return jsonify({'error': 'No active attempt found'}), 404
    
    return calculate_and_submit(attempt, auto_submit=False)

def calculate_and_submit(attempt, auto_submit=False):
    """Calculate score and submit attempt"""
    exam = attempt.exam
    student_answers = attempt.get_answers()
    
    # Calculate score
    correct_count = 0
    total_questions = exam.total_questions
    
    for question in exam.questions:
        student_answer = student_answers.get(str(question.question_number), '').upper()
        if student_answer == question.correct_answer:
            correct_count += 1
    
    # Calculate percentage
    score = correct_count
    percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    # Calculate time taken
    time_taken = int((datetime.utcnow() - attempt.start_time).total_seconds() / 60)
    
    # Update attempt
    attempt.submit_time = datetime.utcnow()
    attempt.score = score
    attempt.percentage = round(percentage, 2)
    attempt.time_taken_minutes = time_taken
    attempt.status = 'auto_submitted' if auto_submit else 'submitted'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Exam submitted successfully' + (' (auto-submitted)' if auto_submit else ''),
        'score': score,
        'total_questions': total_questions,
        'percentage': round(percentage, 2),
        'passed': percentage >= exam.pass_marks,
        'time_taken': time_taken,
        'can_retake': exam.allow_retake
    })

@simple_exams_bp.route('/api/exam/<int:exam_id>/result', methods=['GET'])
@login_required
def get_result(exam_id):
    """Get detailed result with explanations"""
    if get_current_user().role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get last submitted attempt
    attempt = StudentExamAttempt.query.filter_by(
        exam_id=exam_id,
        student_id=get_current_user().id
    ).filter(
        StudentExamAttempt.status.in_(['submitted', 'auto_submitted'])
    ).order_by(StudentExamAttempt.submit_time.desc()).first()
    
    if not attempt:
        return jsonify({'error': 'No submitted attempt found'}), 404
    
    exam = attempt.exam
    student_answers = attempt.get_answers()
    
    # Build detailed results
    question_results = []
    for question in sorted(exam.questions, key=lambda x: x.question_number):
        student_answer = student_answers.get(str(question.question_number), '').upper()
        is_correct = student_answer == question.correct_answer
        
        question_results.append({
            'question_number': question.question_number,
            'question_text': question.question_text,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
            'student_answer': student_answer,
            'correct_answer': question.correct_answer,
            'is_correct': is_correct,
            'explanation': question.explanation
        })
    
    return jsonify({
        'exam': exam.to_dict(),
        'attempt': attempt.to_dict(),
        'questions': question_results
    })
