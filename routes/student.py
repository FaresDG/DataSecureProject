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
    
    # Récupérer les dernières notes
    recent_grades = Grade.query.filter_by(student_id=student.id)\
                              .order_by(Grade.date_recorded.desc())\
                              .limit(5).all()
    
    # Récupérer les absences récentes
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
    
    return render_template('student/grades.html', grades=grades)

@bp.route('/schedule')
@login_required
@student_required
def schedule():
    student = current_user.student_profile
    
    # Récupérer l'emploi du temps pour la classe de l'étudiant
    schedules = Schedule.query.join(Course)\
                             .filter(Schedule.class_group == student.class_name)\
                             .order_by(Schedule.day_of_week, Schedule.start_time).all()
    
    return render_template('student/schedule.html', schedules=schedules)

@bp.route('/absences')
@login_required
@student_required
def absences():
    student = current_user.student_profile
    absences = Absence.query.filter_by(student_id=student.id)\
                           .order_by(Absence.date.desc()).all()
    
    return render_template('student/absences.html', absences=absences)