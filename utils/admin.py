from models import db, Role, User, Student, Parent, Teacher, Administrator, Course, Grade, Absence, Schedule, ParentStudent
from datetime import date, time, datetime
import secrets

def create_sample_data():
    """Crée des données d'exemple pour tester l'application"""
    
    # Créer les rôles s'ils n'existent pas
    roles_data = [
        ('student', 'Étudiant'),
        ('parent', 'Parent'),
        ('teacher', 'Professeur'),
        ('admin', 'Administrateur')
    ]
    
    for role_name, role_desc in roles_data:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=role_desc)
            db.session.add(role)
    
    db.session.commit()
    
    # Récupérer les rôles
    student_role = Role.query.filter_by(name='student').first()
    parent_role = Role.query.filter_by(name='parent').first()
    teacher_role = Role.query.filter_by(name='teacher').first()
    admin_role = Role.query.filter_by(name='admin').first()
    
    # Créer un administrateur par défaut
    if not User.query.filter_by(email='admin@school.fr').first():
        admin_user = User(
            email='admin@school.fr',
            first_name='Admin',
            last_name='Système',
            role_id=admin_role.id,
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        
        admin_profile = Administrator(
            user_id=admin_user.id,
            employee_number='ADM001',
            position='Administrateur Système'
        )
        db.session.add(admin_profile)
    
    # Créer des professeurs
    teachers_data = [
        ('prof.martin@school.fr', 'Jean', 'Martin', 'PROF001', 'Mathématiques'),
        ('prof.durand@school.fr', 'Marie', 'Durand', 'PROF002', 'Français'),
        ('prof.bernard@school.fr', 'Pierre', 'Bernard', 'PROF003', 'Histoire')
    ]
    
    for email, first_name, last_name, emp_num, dept in teachers_data:
        if not User.query.filter_by(email=email).first():
            teacher_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role_id=teacher_role.id,
                is_active=True
            )
            teacher_user.set_password('teacher123')
            db.session.add(teacher_user)
            db.session.commit()
            
            teacher_profile = Teacher(
                user_id=teacher_user.id,
                employee_number=emp_num,
                department=dept,
                hire_date=date.today()
            )
            db.session.add(teacher_profile)
    
    # Créer des étudiants
    students_data = [
        ('gbtexfares@gmail.com', 'Lucas', 'Dupont', 'STU001', '6A'),
        ('etudiant.moreau@school.fr', 'Emma', 'Moreau', 'STU002', '6A'),
        ('etudiant.petit@school.fr', 'Nathan', 'Petit', 'STU003', '6B')
    ]
    
    for email, first_name, last_name, stu_num, class_name in students_data:
        if not User.query.filter_by(email=email).first():
            student_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role_id=student_role.id,
                is_active=True
            )
            student_user.set_password('student123')
            db.session.add(student_user)
            db.session.commit()
            
            student_profile = Student(
                user_id=student_user.id,
                student_number=stu_num,
                class_name=class_name,
                enrollment_date=date.today()
            )
            db.session.add(student_profile)
    
    # Créer des parents
    parents_data = [
        ('parent.dupont@email.fr', 'François', 'Dupont'),
        ('parent.moreau@email.fr', 'Sophie', 'Moreau')
    ]
    
    for email, first_name, last_name in parents_data:
        if not User.query.filter_by(email=email).first():
            parent_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role_id=parent_role.id,
                is_active=True
            )
            parent_user.set_password('parent123')
            db.session.add(parent_user)
            db.session.commit()
            
            parent_profile = Parent(user_id=parent_user.id)
            db.session.add(parent_profile)
    
    db.session.commit()
    
    # Lier parents et enfants
    parent_dupont = Parent.query.join(User).filter(User.email == 'parent.dupont@email.fr').first()
    student_dupont = Student.query.join(User).filter(User.email == 'etudiant.dupont@school.fr').first()
    
    if parent_dupont and student_dupont:
        if not ParentStudent.query.filter_by(parent_id=parent_dupont.id, student_id=student_dupont.id).first():
            parent_student = ParentStudent(
                parent_id=parent_dupont.id,
                student_id=student_dupont.id,
                relationship_type='père'
            )
            db.session.add(parent_student)
    
    # Créer des matières
    courses_data = [
        ('Mathématiques 6ème', 'MATH6', 'Cours de mathématiques niveau 6ème', 4),
        ('Français 6ème', 'FR6', 'Cours de français niveau 6ème', 5),
        ('Histoire 6ème', 'HIST6', 'Cours d\'histoire niveau 6ème', 3)
    ]
    
    teacher_martin = Teacher.query.join(User).filter(User.email == 'prof.martin@school.fr').first()
    teacher_durand = Teacher.query.join(User).filter(User.email == 'prof.durand@school.fr').first()
    teacher_bernard = Teacher.query.join(User).filter(User.email == 'prof.bernard@school.fr').first()
    
    teachers = [teacher_martin, teacher_durand, teacher_bernard]
    
    for i, (name, code, desc, credits) in enumerate(courses_data):
        if not Course.query.filter_by(code=code).first() and teachers[i]:
            course = Course(
                name=name,
                code=code,
                description=desc,
                credits=credits,
                teacher_id=teachers[i].id
            )
            db.session.add(course)
    
    db.session.commit()
    
    print("Données d'exemple créées avec succès !")
    print("Comptes de test créés :")
    print("Admin: admin@school.fr / admin123")
    print("Professeur: prof.martin@school.fr / teacher123") 
    print("Étudiant: etudiant.dupont@school.fr / student123")
    print("Parent: parent.dupont@email.fr / parent123")