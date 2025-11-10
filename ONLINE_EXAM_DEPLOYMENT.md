# Online MCQ Exam System - Deployment Guide

## ✅ What's Been Added

A complete online MCQ exam system has been implemented with the following features:

### Teacher Features
- **Create Exams**: Add up to 40 MCQ questions with 4 options each (A, B, C, D)
- **Manual Entry**: Specify class name, book name, chapter name, duration, pass marks
- **Batch Assignment**: Assign exams to specific batches
- **View Results**: See all student attempts with scores, percentages, and pass/fail status
- **Delete Exams**: Remove exams that are no longer needed
- **Retake Control**: Enable or disable retakes per exam

### Student Features
- **Take Exams**: Answer MCQ questions with a countdown timer
- **Auto-Save**: Answers are automatically saved as you type
- **Auto-Submit**: Exam auto-submits when time runs out
- **Question Navigation**: Jump between questions, see which ones are answered
- **View Results**: See detailed results with correct/wrong answers and explanations
- **Retake Exams**: Retake exams if enabled by teacher

## 📁 Files Created/Modified

### New Files:
1. **models.py** - Added 3 new models:
   - `OnlineExam`: Stores exam metadata (title, class, book, chapter, duration, etc.)
   - `ExamQuestion`: Stores MCQ questions with 4 options and correct answer
   - `StudentExamAttempt`: Stores student attempts with answers (JSON), scores, timing

2. **migrate_add_online_exams.py** - Migration script to create database tables

3. **routes/simple_online_exams.py** - Complete API routes for:
   - Teacher: Create, list, delete exams, view results
   - Student: List exams, start exam, save answers, submit, view results

4. **templates/templates/partials/simple_online_exams_teacher.html** - Teacher UI
5. **templates/templates/partials/simple_online_exams_student.html** - Student UI

### Modified Files:
1. **app.py** - Registered new blueprint `simple_exams_bp`
2. **dashboard_teacher.html** - Added online exams menu item and JavaScript functions
3. **dashboard_student.html** - Added online exams section with Alpine.js component

## 🚀 Deployment Steps for VPS

### Step 1: Pull Latest Code
```bash
cd /var/www/saroyarsir
git pull origin main
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 3: Run Migration
```bash
python migrate_add_online_exams.py
```

Expected output:
```
📚 Creating Online Exam System tables...
✅ Created online_exams table
✅ Created exam_questions table
✅ Created student_exam_attempts table
✅ Online Exam System tables created successfully!
```

### Step 4: Restart Gunicorn
```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

### Step 5: Verify Deployment
```bash
# Check logs for any errors
sudo journalctl -u gunicorn -n 50 --no-pager
```

## 🧪 Testing the System

### As Teacher:
1. Login with teacher account (01762602056 / sir@123@)
2. Click "Online MCQ Exams" in sidebar
3. Click "Create New Exam"
4. Fill in:
   - Exam Title: "Physics Chapter 1 Test"
   - Select Batch
   - Class Name: "HSC 2025"
   - Book Name: "Physics 1st Paper"
   - Chapter Name: "Chapter 1: Motion"
   - Duration: 30 minutes
   - Pass Marks: 40%
   - Allow Retake: Yes
5. Click "Add Question" and add at least 3-5 questions with options
6. Click "Create Exam"
7. Verify exam appears in the list

### As Student:
1. Login with student account (guardian_phone / student123)
2. Click "Online Exams" in sidebar
3. You should see the exam created by teacher
4. Click "Start Exam"
5. Answer questions (answers auto-save)
6. Watch the timer countdown
7. Click "Submit Exam" or wait for auto-submit
8. View results with correct/wrong answers and explanations
9. If retake is enabled, click "Retake Exam" to try again

## 📊 Database Tables

### online_exams
- id, batch_id, title, class_name, book_name, chapter_name
- duration_minutes, total_questions, pass_marks
- created_by (teacher), is_active, allow_retake
- created_at, updated_at

### exam_questions
- id, exam_id, question_number, question_text
- option_a, option_b, option_c, option_d
- correct_answer (A/B/C/D), explanation
- created_at

### student_exam_attempts
- id, exam_id, student_id, attempt_number
- start_time, submit_time
- answers (JSON: {"1": "A", "2": "B", ...})
- score, percentage, status (in_progress/submitted/auto_submitted)
- time_taken_minutes

## 🔗 API Endpoints

### Teacher Endpoints:
- `GET /api/simple-exams/api/simple-exams` - List all exams
- `POST /api/simple-exams/api/simple-exams` - Create exam
- `GET /api/simple-exams/api/simple-exams/:id` - Get exam details
- `DELETE /api/simple-exams/api/simple-exams/:id` - Delete exam
- `GET /api/simple-exams/api/simple-exams/:id/results` - View results
- `GET /api/simple-exams/api/batches-for-exams` - Get batches

### Student Endpoints:
- `GET /api/simple-exams/api/my-exams` - List available exams
- `POST /api/simple-exams/api/exam/:id/start` - Start exam
- `POST /api/simple-exams/api/exam/:id/save-answer` - Save answer
- `POST /api/simple-exams/api/exam/:id/submit` - Submit exam
- `GET /api/simple-exams/api/exam/:id/result` - View result

## ⚙️ System Features

### Auto-Save
- Student answers are automatically saved every time they select an option
- If student closes browser and reopens, they can resume the exam

### Auto-Submit
- JavaScript timer counts down from exam duration
- When timer reaches 0, exam is automatically submitted
- Alert shown to student before auto-submission

### Question Navigation
- Visual grid shows all questions (1-40)
- Green = Answered, Gray = Unanswered, Blue = Current
- Click any question number to jump to it

### Results with Explanations
- Shows correct/wrong for each question
- Green background = Correct answer
- Red background = Student's wrong answer
- Explanation shown below each question (if provided)

### Retake System
- Teacher can enable/disable retakes per exam
- Each attempt is numbered (1, 2, 3, ...)
- All attempts are stored in database
- Results always show latest attempt

## 🐛 Troubleshooting

### Exam not showing for students:
- Check if student is enrolled in the exam's batch
- Verify exam `is_active` is True
- Check if batch enrollment `is_active` is True

### Timer not working:
- Check browser console for JavaScript errors
- Ensure `duration_minutes` is set correctly in database
- Verify start_time is being set when exam starts

### Answers not saving:
- Check network tab in browser dev tools
- Verify `/api/simple-exams/api/exam/:id/save-answer` returns 200
- Check database `student_exam_attempts` table for JSON answers

### Results not showing:
- Ensure exam has been submitted (status = 'submitted' or 'auto_submitted')
- Check if `score` and `percentage` are calculated
- Verify correct_answer matches one of A/B/C/D

## 📝 Usage Notes

1. **Question Limit**: Maximum 40 questions per exam (can be changed in code if needed)
2. **Answer Format**: Only A, B, C, D are accepted (case-insensitive)
3. **Time Format**: Duration is in minutes (5-180 range recommended)
4. **Pass Marks**: Enter as percentage (0-100)
5. **Explanations**: Optional but recommended for student learning

## ✅ System Status

- ✅ Database models created
- ✅ Migration script ready
- ✅ API routes functional
- ✅ Teacher UI complete
- ✅ Student UI complete
- ✅ Timer and auto-submit working
- ✅ Results with explanations
- ✅ Retake functionality
- ✅ Code pushed to GitHub
- ⏳ Ready for VPS deployment

## 🎯 Next Steps

1. SSH into VPS
2. Run deployment steps above
3. Test with teacher account
4. Test with student account
5. Create real exams for students
6. Monitor logs for any issues

---

**Date Created**: November 10, 2025
**Status**: Ready for Production Deployment
**Git Commit**: 35dd0b8 - "Add complete Online MCQ Exam System"
