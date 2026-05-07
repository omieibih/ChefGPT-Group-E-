from flask import Blueprint, render_template, request

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    return render_template("index.html")


@pages_bp.route("/ingredients", methods=["POST"])
def ingredients():
    experience_level = request.form.get("experience_level")
    return render_template("ingredients.html", experience_level=experience_level)


@pages_bp.route("/login")
def login():
    return render_template("login.html")