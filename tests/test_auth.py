import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, Role
from config import config

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        
        # Create base roles
        roles = [
            Role(name='student', description='Student'),
            Role(name='parent', description='Parent'),
            Role(name='teacher', description='Teacher'),
            Role(name='admin', description='Administrator')
        ]
        
        for role in roles:
            db.session.add(role)
        
        db.session.commit()
        
        yield app
        
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class TestAuth:
    def test_login_page_loads(self, client):
        """Test that the login page loads correctly"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_register_page_loads(self, client):
        """Test that the registration page loads correctly"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'sign up' in response.data.lower()

    def test_user_registration(self, client, app):
        """Test registering a new user"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            
            response = client.post('/auth/register', data={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'phone': '0123456789',
                'password': 'StrongPass1!',
                'password2': 'StrongPass1!',
                'role_id': student_role.id,
                'submit': 'Sign up'
            })
            
            # Should redirect to the login page after registration
            assert response.status_code == 302
            
            # Verify that the user was created
            user = User.query.filter_by(email='test@example.com').first()
            assert user is not None
            assert user.first_name == 'Test'
            assert user.last_name == 'User'

    def test_registration_rejects_weak_password(self, client, app):
        """Registration should fail with weak password"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()

            response = client.post('/auth/register', data={
                'email': 'weak@example.com',
                'first_name': 'Weak',
                'last_name': 'User',
                'phone': '0123456789',
                'password': 'weakpass',
                'password2': 'weakpass',
                'role_id': student_role.id,
                'submit': 'Sign up'
            })

            assert response.status_code == 200
            assert User.query.filter_by(email='weak@example.com').first() is None

    def test_user_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/auth/login', data={
            'email': 'invalid@example.com',
            'password': 'wrongpassword',
            'submit': 'Log in'
        })
        
        assert response.status_code == 200
        assert b'incorrect' in response.data.lower()

    def test_user_login_valid_credentials(self, client, app):
        """Test login with valid credentials"""
        with app.app_context():
            # Create a test user
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            user.set_password('StrongPass1!')
            db.session.add(user)
            db.session.commit()
            
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'StrongPass1!',
            'submit': 'Log in'
        })
        
        # Should redirect to MFA verification
        assert response.status_code == 302
        assert '/auth/mfa-verify' in response.location

    def test_mfa_verification(self, client, app):
        """Test MFA verification"""
        with app.app_context():
            # Create a user and simulate pre-MFA state
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            user.set_password('StrongPass1!')
            user.mfa_secret = 'test_mfa_code'
            db.session.add(user)
            db.session.commit()
            
        # Simulate pre-MFA session
        with client.session_transaction() as sess:
            sess['pre_auth_user_id'] = user.id
            
        response = client.post('/auth/mfa-verify', data={
            'code': 'test_mfa_code',
            'submit': 'Verify'
        })
        
        # Should redirect after successful MFA
        assert response.status_code == 302

    def test_logout(self, client, app):
        """Test logging out"""
        with app.app_context():
            # Create and log in a user
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            user.set_password('StrongPass1!')
            db.session.add(user)
            db.session.commit()
            
        # Simulate an active session
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        response = client.get('/auth/logout')
        
        # Should redirect to the home page
        assert response.status_code == 302
        assert '/' in response.location

    def test_password_hashing(self, app):
        """Test that passwords are hashed correctly"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            
            password = 'StrongPass1!'
            user.set_password(password)
            
            # Password should not be stored in plain text
            assert user.password_hash != password
            
            # But should be verifiable
            assert user.check_password(password) is True
            assert user.check_password('wrongpassword') is False

    def test_role_verification(self, app):
        """Test user role verification"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            teacher_role = Role.query.filter_by(name='teacher').first()
            
            student_user = User(
                email='student@example.com',
                first_name='Student',
                last_name='Test',
                role_id=student_role.id
            )
            
            # Test permissions
            assert student_user.has_role('student') is True
            assert student_user.has_role('teacher') is False
            assert student_user.can('view_grades') is True
            assert student_user.can('add_grades') is False

    def test_login_route_resets_invalid_mfa_state(self, client, app):
        """Users with an active session but without MFA verification should be logged out."""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='loop@example.com',
                first_name='Loop',
                last_name='Test',
                role_id=student_role.id
            )
            user.set_password('StrongPass1!')
            user.mfa_verified = False
            db.session.add(user)
            db.session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
