from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # MFA
    mfa_secret = db.Column(db.String(32))
    mfa_verified = db.Column(db.Boolean, default=False)
    
    # Relations
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_mfa_code(self):
        self.mfa_secret = secrets.token_hex(6)
        db.session.commit()
        return self.mfa_secret
    
    def verify_mfa_code(self, code):
        return self.mfa_secret == code
    
    def has_role(self, role_name):
        return self.role.name == role_name
    
    def can(self, permission):
        permissions = {
            'student': ['view_grades', 'view_schedule', 'view_profile'],
            'parent': ['view_child_grades', 'view_child_schedule', 'view_child_absences'],
            'teacher': ['add_grades', 'mark_absences', 'view_classes', 'send_messages'],
            'admin': ['manage_users', 'manage_courses', 'manage_schedule', 'view_dashboard']
        }
        return permission in permissions.get(self.role.name, [])

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_number = db.Column(db.String(20), unique=True, nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    
    user = db.relationship('User', backref='student_profile')
    grades = db.relationship('Grade', backref='student', lazy=True)
    absences = db.relationship('Absence', backref='student', lazy=True)

class Parent(db.Model):
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    user = db.relationship('User', backref='parent_profile')

class ParentStudent(db.Model):
    __tablename__ = 'parent_student'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    relationship_type = db.Column(db.String(50), nullable=False)  # père, mère, tuteur
    
    parent = db.relationship('Parent', backref='children')
    student = db.relationship('Student', backref='parents')

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    
    user = db.relationship('User', backref='teacher_profile')
    courses = db.relationship('Course', backref='teacher', lazy=True)

class Administrator(db.Model):
    __tablename__ = 'administrators'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_number = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    
    user = db.relationship('User', backref='admin_profile')

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=1)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    
    grades = db.relationship('Grade', backref='course', lazy=True)
    schedules = db.relationship('Schedule', backref='course', lazy=True)

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade_value = db.Column(db.Float, nullable=False)
    grade_type = db.Column(db.String(50), nullable=False)  # Contrôle, Examen, Devoir
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    comments = db.Column(db.Text)
    
    teacher = db.relationship('Teacher', backref='grades_given')

class Absence(db.Model):
    __tablename__ = 'absences'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    period = db.Column(db.String(50), nullable=False)  # Matin, Après-midi, Journée
    is_justified = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(200))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    teacher = db.relationship('Teacher', backref='absences_marked')

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)  # Lundi, Mardi, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    classroom = db.Column(db.String(50), nullable=False)
    class_group = db.Column(db.String(50), nullable=False)

class AuthLog(db.Model):
    __tablename__ = 'auth_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # login_attempt, login_success, logout
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, nullable=False)
    details = db.Column(db.Text)
    
    user = db.relationship('User', backref='auth_logs')