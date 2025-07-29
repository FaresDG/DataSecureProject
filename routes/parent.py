from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from models import Grade, Absence, Schedule, Course, Student, ParentStudent

bp = Blueprint('parent', __name__)

def parent_required(f):
    """Décorateur pour vérifier que l'utilisateur est un parent"""
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('parent'):
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@parent_required
def dashboard():
    parent = current_user.parent_profile
    
    # Retrieve the parent's children
    children = Student.query.join(ParentStudent)\
                           .filter(ParentStudent.parent_id == parent.id).all()
    
    # Statistiques pour chaque enfant
    children_data = []
    for child in children:
        recent_grades = Grade.query.filter_by(student_id=child.id)\
                                  .order_by(Grade.date_recorded.desc())\
                                  .limit(3).all()
        
        recent_absences = Absence.query.filter_by(student_id=child.id)\
                                      .order_by(Absence.date.desc())\
                                      .limit(3).all()
        
        children_data.append({
            'student': child,
            'recent_grades': recent_grades,
            'recent_absences': recent_absences,
            'total_grades': Grade.query.filter_by(student_id=child.id).count(),
            'total_absences': Absence.query.filter_by(student_id=child.id).count()
        })
    
    return render_template('parent/dashboard.html', children_data=children_data)

@bp.route('/child/<int:student_id>/grades')
@login_required
@parent_required
def child_grades(student_id):
    # Ensure the child actually belongs to the parent
    parent = current_user.parent_profile
    child = Student.query.join(ParentStudent)\
                        .filter(ParentStudent.parent_id == parent.id,
                               Student.id == student_id).first_or_404()
    
    grades = Grade.query.filter_by(student_id=student_id)\
                       .join(Course)\
                       .order_by(Grade.date_recorded.desc()).all()

    if grades:
        values = [g.grade_value for g in grades]
        average = round(sum(values) / len(values), 1)
        best = round(max(values), 1)
        high_count = len([v for v in values if v >= 16])
        low_count = len([v for v in values if v <= 10])
    else:
        average = best = 0
        high_count = low_count = 0

    return render_template('parent/child_grades.html', child=child, grades=grades,
                           average=average, best=best,
                           high_count=high_count, low_count=low_count)

@bp.route('/child/<int:student_id>/schedule')
@login_required
@parent_required
def child_schedule(student_id):
    parent = current_user.parent_profile
    child = Student.query.join(ParentStudent)\
                        .filter(ParentStudent.parent_id == parent.id,
                               Student.id == student_id).first_or_404()
    
    schedules = Schedule.query.join(Course)\
                             .filter(Schedule.class_group == child.class_name)\
                             .order_by(Schedule.day_of_week, Schedule.start_time).all()

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

    return render_template('parent/child_schedule.html', child=child, events=events)

@bp.route('/child/<int:student_id>/absences')
@login_required
@parent_required
def child_absences(student_id):
    parent = current_user.parent_profile
    child = Student.query.join(ParentStudent)\
                        .filter(ParentStudent.parent_id == parent.id,
                               Student.id == student_id).first_or_404()
    
    absences = Absence.query.filter_by(student_id=student_id)\
                           .order_by(Absence.date.desc()).all()
    
    return render_template('parent/child_absences.html', child=child, absences=absences)