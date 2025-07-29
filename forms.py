from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from models import User, Role, Student, Teacher

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class MFAForm(FlaskForm):
    # Allow codes up to 16 characters for tests and future extensions
    code = StringField('Code de vérification', validators=[DataRequired(), Length(min=6, max=16)])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Vérifier')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Nom', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirmer le mot de passe', 
                             validators=[DataRequired(), EqualTo('password')])
    role_id = SelectField('Rôle', coerce=int, validators=[DataRequired()])
    submit = SubmitField('S\'inscrire')
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Cette adresse email est déjà utilisée.')

class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Nom', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Mot de passe', validators=[Optional(), Length(min=8)])
    role_id = SelectField('Rôle', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Compte actif', default=True)
    submit = SubmitField('Enregistrer')

class GradeForm(FlaskForm):
    student_id = SelectField('Étudiant', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Matière', coerce=int, validators=[DataRequired()])
    grade_value = FloatField('Note', validators=[DataRequired(), NumberRange(min=0, max=20)])
    grade_type = SelectField('Type', choices=[
        ('Contrôle', 'Contrôle'),
        ('Examen', 'Examen'),
        ('Devoir', 'Devoir'),
        ('Participation', 'Participation')
    ], validators=[DataRequired()])
    comments = TextAreaField('Commentaires', validators=[Optional()])
    submit = SubmitField('Ajouter la note')
    
    def __init__(self, *args, **kwargs):
        super(GradeForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [(s.id, f"{s.user.first_name} {s.user.last_name}") 
                                  for s in Student.query.join(User)]

class AbsenceForm(FlaskForm):
    student_id = SelectField('Étudiant', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    period = SelectField('Période', choices=[
        ('Matin', 'Matin'),
        ('Après-midi', 'Après-midi'),
        ('Journée', 'Journée complète')
    ], validators=[DataRequired()])
    is_justified = BooleanField('Absence justifiée', default=False)
    reason = StringField('Motif', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Enregistrer l\'absence')
    
    def __init__(self, *args, **kwargs):
        super(AbsenceForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [(s.id, f"{s.user.first_name} {s.user.last_name}") 
                                  for s in Student.query.join(User)]

class CourseForm(FlaskForm):
    name = StringField('Nom du cours', validators=[DataRequired(), Length(max=100)])
    code = StringField('Code', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description', validators=[Optional()])
    credits = IntegerField('Crédits', validators=[DataRequired(), NumberRange(min=1, max=10)])
    teacher_id = SelectField('Professeur', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Enregistrer')