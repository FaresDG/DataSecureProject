from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Grade, Absence, Course, Student
from forms import GradeForm, AbsenceForm

bp = Blueprint('teacher', __name__)

def teacher_required(f):
    """Décorateur pour vérifier que l'utilisateur est un professeur"""
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('teacher'):
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    teacher = current_user.teacher_profile
    
    # Récupérer les cours du professeur
    courses = Course.query.filter_by(teacher_id=teacher.id).all()
    
    # Statistiques
    total_students = Student.query.join(Grade)\
                                 .filter(Grade.teacher_id == teacher.id)\
                                 .distinct().count()
    total_grades = Grade.query.filter_by(teacher_id=teacher.id).count()
    total_absences = Absence.query.filter_by(teacher_id=teacher.id).count()
    
    return render_template('teacher/dashboard.html',
                         teacher=teacher,
                         courses=courses,
                         total_students=total_students,
                         total_grades=total_grades,
                         total_absences=total_absences)

@bp.route('/courses')
@login_required
@teacher_required
def courses():
    teacher = current_user.teacher_profile
    courses = Course.query.filter_by(teacher_id=teacher.id).all()
    
    return render_template('teacher/courses.html', courses=courses)

@bp.route('/course/<int:course_id>/students')
@login_required
@teacher_required
def course_students(course_id):
    teacher = current_user.teacher_profile
    course = Course.query.filter_by(id=course_id, teacher_id=teacher.id).first_or_404()
    
    # Récupérer les étudiants qui ont des notes dans ce cours
    students = Student.query.join(Grade)\
                           .filter(Grade.course_id == course_id)\
                           .distinct().all()
    
    return render_template('teacher/course_students.html', course=course, students=students)

@bp.route('/add-grade', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_grade():
    teacher = current_user.teacher_profile
    form = GradeForm()
    
    # Populer les choix de cours avec ceux du professeur
    form.course_id.choices = [(c.id, c.name) for c in Course.query.filter_by(teacher_id=teacher.id)]
    
    if form.validate_on_submit():
        grade = Grade(
            student_id=form.student_id.data,
            course_id=form.course_id.data,
            grade_value=form.grade_value.data,
            grade_type=form.grade_type.data,
            teacher_id=teacher.id,
            comments=form.comments.data
        )
        
        db.session.add(grade)
        db.session.commit()
        
        flash('Note ajoutée avec succès !', 'success')
        return redirect(url_for('teacher.courses'))
    
    return render_template('teacher/add_grade.html', form=form)

@bp.route('/mark-absence', methods=['GET', 'POST'])
@login_required
@teacher_required
def mark_absence():
    teacher = current_user.teacher_profile
    form = AbsenceForm()
    
    if form.validate_on_submit():
        absence = Absence(
            student_id=form.student_id.data,
            date=form.date.data,
            period=form.period.data,
            is_justified=form.is_justified.data,
            reason=form.reason.data,
            teacher_id=teacher.id
        )
        
        db.session.add(absence)
        db.session.commit()
        
        flash('Absence enregistrée avec succès !', 'success')
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('teacher/mark_absence.html', form=form)

@bp.route('/grades')
@login_required
@teacher_required
def grades():
    teacher = current_user.teacher_profile
    grades = Grade.query.filter_by(teacher_id=teacher.id)\
                       .join(Course)\
                       .join(Student)\
                       .order_by(Grade.date_recorded.desc()).all()
    
    return render_template('teacher/grades.html', grades=grades)