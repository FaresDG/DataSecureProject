from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.mfa_verified:
        return redirect(url_for('auth.mfa_verify'))
    
    # Redirection vers le dashboard approprié selon le rôle
    role = current_user.role.name
    
    if role == 'student':
        return redirect(url_for('student.dashboard'))
    elif role == 'parent':
        return redirect(url_for('parent.dashboard'))
    elif role == 'teacher':
        return redirect(url_for('teacher.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return render_template('main/dashboard.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')