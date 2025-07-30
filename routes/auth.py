from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from flask_login import login_user, logout_user, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash
import secrets
from datetime import datetime

from models import db, User, AuthLog
from forms import (
    LoginForm,
    MFAForm,
    RegisterForm,
    PasswordResetRequestForm,
    PasswordResetForm,
)
from utils.security import log_auth_attempt

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # If the user somehow has a session but MFA was not completed,
        # logging them out avoids an infinite redirect between the login
        # and verification pages when reopening the site without signing out.
        if not current_user.mfa_verified:
            logout_user()
        else:
            return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if user.is_active:
                # Generate and send the MFA code
                mfa_code = user.generate_mfa_code()
                send_mfa_code(user.email, mfa_code)
                
                session['pre_auth_user_id'] = user.id
                session['mfa_code_sent_at'] = datetime.utcnow().timestamp()
                log_auth_attempt(user.email, 'mfa_code_sent', True, user.id)
                
                flash('A verification code has been sent to your email.', 'info')
                return redirect(url_for('auth.mfa_verify'))
            else:
                log_auth_attempt(form.email.data, 'login_attempt', False, details='Account disabled')
                flash('Your account has been disabled.', 'danger')
        else:
            log_auth_attempt(form.email.data, 'login_attempt', False, details='Invalid credentials')
            flash('Incorrect email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@bp.route('/mfa-verify', methods=['GET', 'POST'])
def mfa_verify():
    if 'pre_auth_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    form = MFAForm()
    if form.validate_on_submit():
        user = User.query.get(session['pre_auth_user_id'])

        sent_at = session.get('mfa_code_sent_at')
        if not sent_at or (datetime.utcnow().timestamp() - sent_at) > 120:
            log_auth_attempt(user.email if user else 'unknown', 'mfa_expired', False,
                           user.id if user else None)
            session.pop('pre_auth_user_id', None)
            session.pop('mfa_code_sent_at', None)
            flash('The verification code has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))

        if user and user.verify_mfa_code(form.code.data):
            user.mfa_verified = True
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=form.remember_me.data)
            session.pop('pre_auth_user_id', None)
            session.pop('mfa_code_sent_at', None)
            
            log_auth_attempt(user.email, 'login_success', True, user.id)
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            log_auth_attempt(user.email if user else 'unknown', 'mfa_failed', False,
                           details='Incorrect MFA code')
            flash('Invalid verification code.', 'danger')
    
    return render_template('auth/mfa_verify.html', form=form)

@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        log_auth_attempt(current_user.email, 'logout', True, current_user.id)
        current_user.mfa_verified = False
        db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role_id=form.role_id.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@bp.route('/reset-request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('If an account exists for that email, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    user = User.verify_reset_token(token)
    if not user:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.reset_request'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

def send_mfa_code(email, code):
    """Send the MFA code via email"""
    try:
        msg = Message(
            subject='Verification code - François Mitterrand Middle School',
            recipients=[email],
            body=f'''
Hello,

Your verification code to access the François Mitterrand Middle School intranet is: {code}

This code expires in 2 minutes.

If you did not request this code, please ignore this message.

Regards,
The François Mitterrand Middle School intranet team
            '''
        )
        mail = current_app.extensions.get('mail')
        if not mail:
            current_app.logger.error('Flask-Mail not initialized')
            return False
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending MFA email: {e}")
        return False


def send_password_reset_email(user):
    """Send a password reset email"""
    try:
        token = user.get_reset_token()
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        msg = Message(
            subject='Password reset - François Mitterrand Middle School',
            recipients=[user.email],
            body=f'''
Hello,

To reset your password, click the link below:
{reset_url}

This link expires in 1 hour.

If you did not request this, please ignore this email.

Regards,
The François Mitterrand Middle School intranet team
            '''
        )
        mail = current_app.extensions.get('mail')
        if not mail:
            current_app.logger.error('Flask-Mail not initialized')
            return False
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending reset email: {e}")
        return False