import pytest
from datetime import date, datetime
from app import create_app
from models import db, User, Role, Student, Teacher, Course, Grade

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        
        # Créer les rôles de base
        roles = [
            Role(name='student', description='Étudiant'),
            Role(name='teacher', description='Professeur')
        ]
        
        for role in roles:
            db.session.add(role)
        
        db.session.commit()
        
        yield app
        
        db.drop_all()

class TestModels:
    def test_user_creation(self, app):
        """Test la création d'un utilisateur"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            
            user = User(
                email='test@example.com',
                first_name='John',
                last_name='Doe',
                role_id=student_role.id
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            saved_user = User.query.filter_by(email='test@example.com').first()
            assert saved_user is not None
            assert saved_user.first_name == 'John'
            assert saved_user.check_password('password123') is True

    def test_student_creation(self, app):
        """Test la création d'un profil étudiant"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            
            user = User(
                email='student@example.com',
                first_name='Jane',
                last_name='Student',
                role_id=student_role.id
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            student = Student(
                user_id=user.id,
                student_number='STU001',
                class_name='6A',
                enrollment_date=date.today()
            )
            db.session.add(student)
            db.session.commit()
            
            saved_student = Student.query.filter_by(student_number='STU001').first()
            assert saved_student is not None
            assert saved_student.user.first_name == 'Jane'
            assert saved_student.class_name == '6A'

    def test_teacher_creation(self, app):
        """Test la création d'un profil professeur"""
        with app.app_context():
            teacher_role = Role.query.filter_by(name='teacher').first()
            
            user = User(
                email='teacher@example.com',
                first_name='Bob',
                last_name='Teacher',
                role_id=teacher_role.id
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            teacher = Teacher(
                user_id=user.id,
                employee_number='PROF001',
                department='Mathematics',
                hire_date=date.today()
            )
            db.session.add(teacher)
            db.session.commit()
            
            saved_teacher = Teacher.query.filter_by(employee_number='PROF001').first()
            assert saved_teacher is not None
            assert saved_teacher.user.first_name == 'Bob'
            assert saved_teacher.department == 'Mathematics'

    def test_course_creation(self, app):
        """Test la création d'un cours"""
        with app.app_context():
            teacher_role = Role.query.filter_by(name='teacher').first()
            
            # Créer un professeur
            user = User(
                email='teacher@example.com',
                first_name='Alice',
                last_name='Professor',
                role_id=teacher_role.id
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            teacher = Teacher(
                user_id=user.id,
                employee_number='PROF001',
                department='Science',
                hire_date=date.today()
            )
            db.session.add(teacher)
            db.session.commit()
            
            # Créer un cours
            course = Course(
                name='Physics 101',
                code='PHY101',
                description='Introduction to Physics',
                credits=3,
                teacher_id=teacher.id
            )
            db.session.add(course)
            db.session.commit()
            
            saved_course = Course.query.filter_by(code='PHY101').first()
            assert saved_course is not None
            assert saved_course.name == 'Physics 101'
            assert saved_course.teacher.user.first_name == 'Alice'

    def test_grade_creation(self, app):
        """Test la création d'une note"""
        with app.app_context():
            # Créer les rôles nécessaires
            student_role = Role.query.filter_by(name='student').first()
            teacher_role = Role.query.filter_by(name='teacher').first()
            
            # Créer un étudiant
            student_user = User(
                email='student@example.com',
                first_name='John',
                last_name='Student',
                role_id=student_role.id
            )
            student_user.set_password('password123')
            db.session.add(student_user)
            db.session.commit()
            
            student = Student(
                user_id=student_user.id,
                student_number='STU001',
                class_name='6A',
                enrollment_date=date.today()
            )
            db.session.add(student)
            db.session.commit()
            
            # Créer un professeur
            teacher_user = User(
                email='teacher@example.com',
                first_name='Alice',
                last_name='Teacher',
                role_id=teacher_role.id
            )
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.commit()
            
            teacher = Teacher(
                user_id=teacher_user.id,
                employee_number='PROF001',
                department='Math',
                hire_date=date.today()
            )
            db.session.add(teacher)
            db.session.commit()
            
            # Créer un cours
            course = Course(
                name='Mathematics 101',
                code='MATH101',
                description='Basic Mathematics',
                credits=3,
                teacher_id=teacher.id
            )
            db.session.add(course)
            db.session.commit()
            
            # Créer une note
            grade = Grade(
                student_id=student.id,
                course_id=course.id,
                grade_value=15.5,
                grade_type='Contrôle',
                teacher_id=teacher.id,
                comments='Bon travail'
            )
            db.session.add(grade)
            db.session.commit()
            
            saved_grade = Grade.query.filter_by(student_id=student.id).first()
            assert saved_grade is not None
            assert saved_grade.grade_value == 15.5
            assert saved_grade.grade_type == 'Contrôle'
            assert saved_grade.student.user.first_name == 'John'
            assert saved_grade.course.name == 'Mathematics 101'

    def test_user_role_permissions(self, app):
        """Test les permissions basées sur les rôles"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            teacher_role = Role.query.filter_by(name='teacher').first()
            
            student_user = User(
                email='student@example.com',
                first_name='Student',
                last_name='Test',
                role_id=student_role.id
            )
            
            teacher_user = User(
                email='teacher@example.com',
                first_name='Teacher',
                last_name='Test',
                role_id=teacher_role.id
            )
            
            # Test permissions étudiants
            assert student_user.can('view_grades') is True
            assert student_user.can('add_grades') is False
            assert student_user.can('manage_users') is False
            
            # Test permissions professeurs
            assert teacher_user.can('view_grades') is False
            assert teacher_user.can('add_grades') is True
            assert teacher_user.can('manage_users') is False

    def test_mfa_code_generation(self, app):
        """Test la génération et vérification des codes MFA"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            db.session.add(user)
            db.session.commit()
            
            # Générer un code MFA
            mfa_code = user.generate_mfa_code()
            
            assert mfa_code is not None
            assert len(mfa_code) == 12  # 6 bytes en hex = 12 caractères
            assert user.mfa_secret == mfa_code
            
            # Vérifier le code
            assert user.verify_mfa_code(mfa_code) is True
            assert user.verify_mfa_code('wrong_code') is False