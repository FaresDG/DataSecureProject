from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import (
    User,
    Student,
    Parent,
    ParentStudent,
    Teacher,
    Administrator,
    Course,
    Grade,
)

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("main/index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    if not current_user.mfa_verified:
        return redirect(url_for("auth.mfa_verify"))

    # Redirection vers le dashboard approprié selon le rôle
    role = current_user.role.name

    if role == "student":
        return redirect(url_for("student.dashboard"))
    elif role == "parent":
        return redirect(url_for("parent.dashboard"))
    elif role == "teacher":
        return redirect(url_for("teacher.dashboard"))
    elif role == "admin":
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template("main/dashboard.html")


@bp.route("/profile")
@login_required
def profile():
    role = current_user.role.name
    context = {"role": role}

    if role == "student":
        context["student"] = current_user.student_profile
    elif role == "parent":
        parent = current_user.parent_profile
        children = (
            Student.query.join(ParentStudent)
            .filter(ParentStudent.parent_id == parent.id)
            .all()
        )
        context["children"] = children
    elif role == "teacher":
        teacher = current_user.teacher_profile
        courses = Course.query.filter_by(teacher_id=teacher.id).all()
        context["teacher"] = teacher
        context["courses"] = courses
    elif role == "admin":
        stats = {
            "total_users": User.query.count(),
            "total_students": Student.query.count(),
            "total_teachers": Teacher.query.count(),
            "total_parents": Parent.query.count(),
            "total_courses": Course.query.count(),
            "total_grades": Grade.query.count(),
        }
        context["stats"] = stats

    return render_template("main/profile.html", **context)
