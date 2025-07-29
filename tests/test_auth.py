import pytest
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
        
        # Créer les rôles de base
        roles = [
            Role(name='student', description='Étudiant'),
            Role(name='parent', description='Parent'),
            Role(name='teacher', description='Professeur'),
            Role(name='admin', description='Administrateur')
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
        """Test que la page de connexion se charge correctement"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_register_page_loads(self, client):
        """Test que la page d'inscription se charge correctement"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'sign up' in response.data.lower()

    def test_user_registration(self, client, app):
        """Test l'inscription d'un nouvel utilisateur"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            
            response = client.post('/auth/register', data={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'phone': '0123456789',
                'password': 'testpassword123',
                'password2': 'testpassword123',
                'role_id': student_role.id,
                'submit': 'Sign up'
            })
            
            # Doit rediriger vers la page de connexion après inscription
            assert response.status_code == 302
            
            # Vérifier que l'utilisateur a été créé
            user = User.query.filter_by(email='test@example.com').first()
            assert user is not None
            assert user.first_name == 'Test'
            assert user.last_name == 'User'

    def test_user_login_invalid_credentials(self, client):
        """Test connexion avec des identifiants invalides"""
        response = client.post('/auth/login', data={
            'email': 'invalid@example.com',
            'password': 'wrongpassword',
            'submit': 'Log in'
        })
        
        assert response.status_code == 200
        assert b'incorrect' in response.data.lower()

    def test_user_login_valid_credentials(self, client, app):
        """Test connexion avec des identifiants valides"""
        with app.app_context():
            # Créer un utilisateur de test
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            user.set_password('testpassword123')
            db.session.add(user)
            db.session.commit()
            
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword123',
            'submit': 'Log in'
        })
        
        # Doit rediriger vers la vérification MFA
        assert response.status_code == 302
        assert '/auth/mfa-verify' in response.location

    def test_mfa_verification(self, client, app):
        """Test la vérification MFA"""
        with app.app_context():
            # Créer un utilisateur et simuler l'état pré-MFA
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            user.set_password('testpassword123')
            user.mfa_secret = 'test_mfa_code'
            db.session.add(user)
            db.session.commit()
            
        # Simuler la session pré-MFA
        with client.session_transaction() as sess:
            sess['pre_auth_user_id'] = user.id
            
        response = client.post('/auth/mfa-verify', data={
            'code': 'test_mfa_code',
            'submit': 'Verify'
        })
        
        # Doit rediriger après MFA réussi
        assert response.status_code == 302

    def test_logout(self, client, app):
        """Test la déconnexion"""
        with app.app_context():
            # Créer et connecter un utilisateur
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            user.set_password('testpassword123')
            db.session.add(user)
            db.session.commit()
            
        # Simuler une session active
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        response = client.get('/auth/logout')
        
        # Doit rediriger vers la page d'accueil
        assert response.status_code == 302
        assert '/' in response.location

    def test_password_hashing(self, app):
        """Test que les mots de passe sont correctement hachés"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=student_role.id
            )
            
            password = 'testpassword123'
            user.set_password(password)
            
            # Le mot de passe ne doit pas être stocké en clair
            assert user.password_hash != password
            
            # Mais doit pouvoir être vérifié
            assert user.check_password(password) is True
            assert user.check_password('wrongpassword') is False

    def test_role_verification(self, app):
        """Test la vérification des rôles utilisateur"""
        with app.app_context():
            student_role = Role.query.filter_by(name='student').first()
            teacher_role = Role.query.filter_by(name='teacher').first()
            
            student_user = User(
                email='student@example.com',
                first_name='Student',
                last_name='Test',
                role_id=student_role.id
            )
            
            # Test des permissions
            assert student_user.has_role('student') is True
            assert student_user.has_role('teacher') is False
            assert student_user.can('view_grades') is True
            assert student_user.can('add_grades') is False