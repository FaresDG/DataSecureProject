from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Grade, Absence, Schedule, Course

bp = Blueprint('student', __name__)

def student_required(f):
    """Décorateur pour vérifier que l'utilisateur est un étudiant"""
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('student'):
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    student = current_user.student_profile
    
    # Retrieve latest grades
    recent_grades = Grade.query.filter_by(student_id=student.id)\
                              .order_by(Grade.date_recorded.desc())\
                              .limit(5).all()
    
    # Retrieve recent absences
    recent_absences = Absence.query.filter_by(student_id=student.id)\
                                  .order_by(Absence.date.desc())\
                                  .limit(5).all()
    
    # Statistiques
    total_grades = Grade.query.filter_by(student_id=student.id).count()
    total_absences = Absence.query.filter_by(student_id=student.id).count()
    
    return render_template('student/dashboard.html',
                         student=student,
                         recent_grades=recent_grades,
                         recent_absences=recent_absences,
                         total_grades=total_grades,
                         total_absences=total_absences)

@bp.route('/grades')
@login_required
@student_required
def grades():
    student = current_user.student_profile
    grades = Grade.query.filter_by(student_id=student.id)\
                       .join(Course)\
                       .order_by(Grade.date_recorded.desc()).all()

    # Basic statistics for UI summary
    if grades:
        values = [g.grade_value for g in grades]
        average = round(sum(values) / len(values), 1)
        best = round(max(values), 1)
        high_count = len([v for v in values if v >= 16])
        low_count = len([v for v in values if v <= 10])
    else:
        average = best = 0
        high_count = low_count = 0

    return render_template('student/grades.html', grades=grades,
                           average=average, best=best,
                           high_count=high_count, low_count=low_count)

@bp.route('/schedule')
@login_required
@student_required
def schedule():
    student = current_user.student_profile

    # Get the schedule for the student's class
    schedules = Schedule.query.join(Course)\
                             .filter(Schedule.class_group == student.class_name)\
                             .order_by(Schedule.day_of_week, Schedule.start_time).all()

    # Convert schedule objects to a format usable by the calendar
    day_map = {
        'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
        'Thursday': 4, 'Friday': 5, 'Saturday': 6,
        'Sunday': 0
    }
    events = [
        {
            'title': f"{s.course.name} ({s.classroom})",
            'daysOfWeek': [day_map.get(s.day_of_week, 0)],
            'startTime': s.start_time.strftime('%H:%M'),
            'endTime': s.end_time.strftime('%H:%M')
        }
        for s in schedules
    ]

    return render_template('student/schedule.html', events=events)

@bp.route('/absences')
@login_required
@student_required
def absences():
    student = current_user.student_profile
    absences = Absence.query.filter_by(student_id=student.id)\
                           .order_by(Absence.date.desc()).all()
    
    return render_template('student/absences.html', absences=absences)