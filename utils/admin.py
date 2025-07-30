from models import (
    db,
    Role,
    User,
    Student,
    Parent,
    Teacher,
    Administrator,
    Course,
    Grade,
    Absence,
    Schedule,
    ParentStudent,
)
from datetime import date, time, datetime, timedelta
import random


def create_sample_data():
    """Populate the database with a large sample dataset."""

    # Roles
    roles = {
        "student": "Student",
        "parent": "Parent",
        "teacher": "Teacher",
        "admin": "Administrator",
    }
    for rname, desc in roles.items():
        if not Role.query.filter_by(name=rname).first():
            db.session.add(Role(name=rname, description=desc))
    db.session.commit()

    student_role = Role.query.filter_by(name="student").first()
    parent_role = Role.query.filter_by(name="parent").first()
    teacher_role = Role.query.filter_by(name="teacher").first()
    admin_role = Role.query.filter_by(name="admin").first()

    # Predefined accounts for testing
    if not User.query.filter_by(email="ulbis047@gmail.com").first():
        user = User(
            email="ulbis047@gmail.com",
            first_name="Catherine",
            last_name="SPOOKIE",
            role_id=admin_role.id,
            is_active=True,
            phone="0102030405",
            address="02 route de Duclair Canteleu",
            birthdate=date(1980, 1, 1),
        )
        user.set_password("admin123")
        user.avatar_filename = "Catherine_SPOOKIE.png"
        db.session.add(user)
        db.session.commit()
        admin_profile = Administrator(
            user_id=user.id, employee_number="ADM900", position="Administrator"
        )
        db.session.add(admin_profile)
        db.session.commit()
    # Administrators
    for i in range(1, 4):
        email = f"admin{i}@school.fr"
        if not User.query.filter_by(email=email).first():
            user = User(
                email=email,
                first_name=f"Admin{i}",
                last_name="School",
                role_id=admin_role.id,
                is_active=True,
                phone="0102030405",
                address="1 Admin Way",
                birthdate=date(1980, 1, 1),
            )
            user.set_password("admin123")
            db.session.add(user)
            db.session.commit()
            admin = Administrator(
                user_id=user.id, employee_number=f"ADM{i:03d}", position="Administrator"
            )
            db.session.add(admin)
    db.session.commit()

    # Teachers
    teachers = []
    for i in range(1, 31):
        email = f"teacher{i}@school.fr"
        if not User.query.filter_by(email=email).first():
            user = User(
                email=email,
                first_name=f"Teacher{i}",
                last_name="Demo",
                role_id=teacher_role.id,
                is_active=True,
                phone="0102030405",
                address="1 Teacher St",
                birthdate=date(1985, 1, 1),
            )
            user.set_password("teacher123")
            db.session.add(user)
            db.session.commit()
            teacher = Teacher(
                user_id=user.id,
                employee_number=f"TCH{i:03d}",
                department="General",
                hire_date=date.today(),
            )
            db.session.add(teacher)
            teachers.append(teacher)
        else:
            teachers.append(
                Teacher.query.join(User).filter(User.email == email).first()
            )
    db.session.commit()

    # Specific teacher for testing
    if not User.query.filter_by(email="gbtexfares@gmail.com").first():
        user = User(
            email="gbtexfares@gmail.com",
            first_name="Thomas",
            last_name="LECERIER",
            role_id=teacher_role.id,
            is_active=True,
            phone="0102030405",
            address="33 route avenue du docteur planet La Rochelle",
            birthdate=date(1995, 4, 11),
        )
        user.set_password("teacher123")
        user.avatar_filename = "Thomas_LECERIER.png"
        db.session.add(user)
        db.session.commit()
        teacher_profile = Teacher(
            user_id=user.id,
            employee_number="TCH900",
            department="General",
            hire_date=date.today(),
        )
        db.session.add(teacher_profile)
        teachers.append(teacher_profile)
        db.session.commit()
    else:
        teachers.append(
            Teacher.query.join(User)
            .filter(User.email == "gbtexfares@gmail.com")
            .first()
        )
    # Students
    class_groups = [
        "6A",
        "6B",
        "6C",
        "5A",
        "5B",
        "5C",
        "4A",
        "4B",
        "4C",
        "3A",
        "3B",
        "3C",
    ]
    students = []
    for i in range(1, 101):
        email = f"student{i}@school.fr"
        if not User.query.filter_by(email=email).first():
            if i == 1:
                # Custom student profile for Prune Laguerre
                first_name = "Prune"
                last_name = "LAGUERRE"
                address = "24 rue de vaux de Foletier La Rochelle"
                birth = date(2015, 10, 1)
            else:
                first_name = f"Student{i}"
                last_name = "Demo"
                address = "1 Student Rd"
                birth = date(2010, 1, 1)

            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role_id=student_role.id,
                is_active=True,
                phone="0102030405",
                address=address,
                birthdate=birth,
            )
            user.set_password("student123")
            if i == 1:
                user.avatar_filename = "Prune_LAGUERRE.png"
            db.session.add(user)
            db.session.commit()
            profile = Student(
                user_id=user.id,
                student_number=f"STU{i:03d}",
                class_name=random.choice(class_groups),
                enrollment_date=date.today(),
            )
            db.session.add(profile)
            students.append(profile)
        else:
            students.append(
                Student.query.join(User).filter(User.email == email).first()
            )
    db.session.commit()

    # Specific student for testing
    if not User.query.filter_by(email="dossoufares@gmail.com").first():
        user = User(
            email="dossoufares@gmail.com",
            first_name="Richard",
            last_name="LAGUERRE",
            role_id=student_role.id,
            is_active=True,
            phone="0102030405",
            address="24 rue de vaux de Foletier La Rochelle",
            birthdate=date(2015, 11, 1),
        )
        user.set_password("student123")
        user.avatar_filename = "Richard_LAGUERRE.png"
        db.session.add(user)
        db.session.commit()
        student_profile = Student(
            user_id=user.id,
            student_number="STU900",
            class_name="6A",
            enrollment_date=date.today(),
        )
        db.session.add(student_profile)
        students.append(student_profile)
        db.session.commit()
    else:
        students.append(
            Student.query.join(User)
            .filter(User.email == "dossoufares@gmail.com")
            .first()
        )
    # Parents
    parents = []
    for i in range(1, 51):
        email = f"parent{i}@mail.fr"
        if not User.query.filter_by(email=email).first():
            user = User(
                email=email,
                first_name=f"Parent{i}",
                last_name="Demo",
                role_id=parent_role.id,
                is_active=True,
                phone="0102030405",
                address="1 Parent Ave",
                birthdate=date(1980, 1, 1),
            )
            user.set_password("parent123")
            db.session.add(user)
            db.session.commit()
            profile = Parent(user_id=user.id)
            db.session.add(profile)
            parents.append(profile)
        else:
            parents.append(Parent.query.join(User).filter(User.email == email).first())
    db.session.commit()

    # Specific parent for testing
    if not User.query.filter_by(email="mlalarochelle17x@gmail.com").first():
        user = User(
            email="mlalarochelle17x@gmail.com",
            first_name="Chauvet",
            last_name="LAGUERRE",
            role_id=parent_role.id,
            is_active=True,
            phone="0102030405",
            address="24 rue de vaux de Foletier La Rochelle",
            birthdate=date(1975, 11, 1),
        )
        user.set_password("parent123")
        user.avatar_filename = "Chauvet_LAGUERRE.png"
        db.session.add(user)
        db.session.commit()
        parent_profile = Parent(user_id=user.id)
        db.session.add(parent_profile)
        parents.append(parent_profile)
        db.session.commit()
        if (
            students
            and not ParentStudent.query.filter_by(
                parent_id=parent_profile.id, student_id=students[0].id
            ).first()
        ):
            link = ParentStudent(
                parent_id=parent_profile.id,
                student_id=students[0].id,
                relationship_type="parent",
            )
            db.session.add(link)
            db.session.commit()
    else:
        parent_profile = (
            Parent.query.join(User)
            .filter(User.email == "mlalarochelle17x@gmail.com")
            .first()
        )
        parents.append(parent_profile)
    # Link parents to students (2 students per parent when possible)
    for idx, parent in enumerate(parents):
        child_indices = [idx * 2, idx * 2 + 1]
        for ci in child_indices:
            if ci < len(students):
                if not ParentStudent.query.filter_by(
                    parent_id=parent.id, student_id=students[ci].id
                ).first():
                    link = ParentStudent(
                        parent_id=parent.id,
                        student_id=students[ci].id,
                        relationship_type="parent",
                    )
                    db.session.add(link)
    db.session.commit()

    # Courses
    course_names = [
        "French",
        "Mathematics",
        "History-Geography",
        "Civics",
        "Foreign Languages",
        "Biology",
        "Physics-Chemistry",
        "Technology",
        "Physical Education",
        "Art",
        "Music",
    ]
    courses = []
    for idx, name in enumerate(course_names, start=1):
        code = f"COUR{idx:03d}"
        if not Course.query.filter_by(code=code).first():
            teacher = teachers[(idx - 1) % len(teachers)]
            course = Course(
                name=name,
                code=code,
                description=f"Course on {name}",
                credits=1,
                teacher_id=teacher.id,
            )
            db.session.add(course)
            courses.append(course)
        else:
            courses.append(Course.query.filter_by(code=code).first())
    db.session.commit()

    # Schedules (one random slot per course and class)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = [
        (time(8, 0), time(9, 0)),
        (time(9, 0), time(10, 0)),
        (time(10, 0), time(11, 0)),
        (time(11, 0), time(12, 0)),
    ]
    for course in courses:
        for group in class_groups:
            start, end = random.choice(time_slots)
            sched = Schedule(
                course_id=course.id,
                day_of_week=random.choice(days),
                start_time=start,
                end_time=end,
                classroom=f"{random.randint(1,20)}A",
                class_group=group,
            )
            db.session.add(sched)
    db.session.commit()

    # Grades (one grade per student per course)
    for student in students:
        for course in courses:
            grade = Grade(
                student_id=student.id,
                course_id=course.id,
                grade_value=round(random.uniform(5, 20), 2),
                grade_type="Test",
                date_recorded=datetime.utcnow(),
                teacher_id=course.teacher_id,
                comments="",
            )
            db.session.add(grade)
    db.session.commit()

    # Absences (0-2 random absences per student)
    for student in students:
        for _ in range(random.randint(0, 2)):
            absence = Absence(
                student_id=student.id,
                date=date.today() - timedelta(days=random.randint(1, 30)),
                period="Day",
                is_justified=random.choice([True, False]),
                reason="Illness",
                teacher_id=random.choice(teachers).id,
            )
            db.session.add(absence)
    db.session.commit()

    print("Sample data created")
