from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from models import User, Role, Student, Teacher

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')

class MFAForm(FlaskForm):
    # Allow codes up to 16 characters for tests and future extensions
    code = StringField('Verification code', validators=[DataRequired(), Length(min=6, max=16)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Verify')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm password',
                             validators=[DataRequired(), EqualTo('password')])
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Sign up')
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email address is already in use.')

class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[Optional(), Length(min=8)])
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Active account', default=True)
    submit = SubmitField('Save')

class GradeForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    grade_value = FloatField('Grade', validators=[DataRequired(), NumberRange(min=0, max=20)])
    grade_type = SelectField('Type', choices=[
        ('Test', 'Test'),
        ('Exam', 'Exam'),
        ('Homework', 'Homework'),
        ('Participation', 'Participation')
    ], validators=[DataRequired()])
    comments = TextAreaField('Comments', validators=[Optional()])
    submit = SubmitField('Add grade')
    
    def __init__(self, *args, **kwargs):
        super(GradeForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [(s.id, f"{s.user.first_name} {s.user.last_name}") 
                                  for s in Student.query.join(User)]

class AbsenceForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    period = SelectField('Period', choices=[
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Day', 'Full day')
    ], validators=[DataRequired()])
    is_justified = BooleanField('Justified absence', default=False)
    reason = StringField('Reason', validators=[Optional(), Length(max=200)])
    submit = SubmitField("Save absence")
    
    def __init__(self, *args, **kwargs):
        super(AbsenceForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [(s.id, f"{s.user.first_name} {s.user.last_name}") 
                                  for s in Student.query.join(User)]

class CourseForm(FlaskForm):
    name = StringField('Course name', validators=[DataRequired(), Length(max=100)])
    code = StringField('Code', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description', validators=[Optional()])
    credits = IntegerField('Credits', validators=[DataRequired(), NumberRange(min=1, max=10)])
    teacher_id = SelectField('Teacher', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save')