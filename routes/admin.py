from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, Student, Parent, Teacher, Administrator, Course, Grade, Absence, Role
from forms import UserForm, CourseForm
from utils.admin import create_sample_data

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to ensure the user is an administrator"""
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('admin'):
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Global statistics
    stats = {
        'total_users': User.query.count(),
        'total_students': Student.query.count(),
        'total_teachers': Teacher.query.count(),
        'total_parents': Parent.query.count(),
        'total_courses': Course.query.count(),
        'total_grades': Grade.query.count(),
        'total_absences': Absence.query.count()
    }
    
    # Latest activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_grades = Grade.query.order_by(Grade.date_recorded.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         recent_grades=recent_grades)

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserForm()
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role_id=form.role_id.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html', form=form)

@bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        user.role_id = form.role_id.data
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/courses')
@login_required
@admin_required
def courses():
    courses = Course.query.join(Teacher).join(User).all()
    return render_template('admin/courses.html', courses=courses)

@bp.route('/course/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    form = CourseForm()
    form.teacher_id.choices = [(t.id, f"{t.user.first_name} {t.user.last_name}") 
                              for t in Teacher.query.join(User)]
    
    if form.validate_on_submit():
        course = Course(
            name=form.name.data,
            code=form.code.data,
            description=form.description.data,
            credits=form.credits.data,
            teacher_id=form.teacher_id.data
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/add_course.html', form=form)

@bp.route('/init-sample-data')
@login_required
@admin_required
def init_sample_data():
    """Initialize sample data for testing"""
    try:
        create_sample_data()
        flash('Sample data created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating sample data: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))