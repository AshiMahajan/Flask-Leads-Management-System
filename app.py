from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from sqlalchemy import func
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///salon.db"
app.config["SECRET_KEY"] = "abczyx"

db = SQLAlchemy(app)


class Employees(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    option = db.Column(db.String, nullable=False)

    def __init__(self, username, email, password, option):
        self.username = username
        self.email = email
        self.password = password
        self.option = option


class Managers(db.Model):
    __tablename__ = "managers"
    id = db.Column(db.Integer, primary_key=True)
    lead_name = db.Column(db.String, nullable=False)
    service = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    query = db.Column(db.String, nullable=False)
    field = db.Column(db.String, nullable=False)

    def __init__(self, lead_name, service, phone_number, query, field):
        self.lead_name = lead_name
        self.service = service
        self.phone_number = phone_number
        self.query = query
        self.field = field


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    lead_name = db.Column(db.String, nullable=False)
    service = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    query = db.Column(db.String, nullable=False)

    def __init__(self, lead_name, service, phone_number, query):
        self.lead_name = lead_name
        self.service = service
        self.phone_number = phone_number
        self.query = query


def save_user(username, email, password, option):
    if Employees.query.filter_by(email=email).first():
        flash("Email already exists.", "error")
        return False
    user = Employees(username=username, email=email, password=password, option=option)
    db.session.add(user)
    db.session.commit()
    return True


def save_contact(service, phone_number, query):
    if Users.query.filter_by(phone_number=phone_number).first():
        flash("Phone number already exists.", "error")
        return False
    contact = Users(service=service, phone_number=phone_number, query=query)
    db.session.add(contact)
    db.session.commit()
    return True


def check_user(email, password):
    user = Employees.query.filter_by(email=email, password=password).first()
    if user:
        return user.username, user.option
    return None, None


def is_manager(email):
    user = Employees.query.filter_by(email=email, option="manager").first()
    return bool(user)


@app.route("/home")
def hello_world():
    return render_template("home.html")


##### SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username, email, password, option = (
            request.form["username"],
            request.form["email"],
            request.form["password"],
            request.form["options"],
        )
        if (
            (option == "admin" and not email.endswith("@marvel.com"))
            or (option == "user" and email.endswith("@marvel.com"))
            or (option == "manager" and not email.endswith("@manager.com"))
        ):
            flash(f"Invalid email for {option} option!", "error")
        elif not (8 <= len(password) <= 13):
            flash("Password must be between 8 to 13 characters!", "error")
        elif save_user(username, email, password, option):
            flash(
                Markup(
                    'Account created! <a href="/login" class="alert-link">Login</a> now'
                ),
                "success",
            )
            return redirect(url_for("signup"))

        return render_template(
            "signup.html", username=username, email=email, option=option
        )

    return render_template("signup.html")


##### LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        username, user_option = check_user(email, password)
        if user_option:
            session.update(
                {"username": username, "email": email, "user_option": user_option}
            )
            return redirect(
                url_for("login_user" if user_option == "user" else "login_admin")
            )
        else:
            flash(
                Markup(
                    'Email or password incorrect! <a href="/signup" class="alert-link"> Signup </a>instead'
                ),
                "success",
            )
    return render_template("login.html")


@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        lead_name = request.form.get("lead_name")
        service = request.form.get("service")
        phone_number = request.form.get("phone_number")
        query = request.form.get("query")

        contact = Users(
            lead_name=lead_name, service=service, phone_number=phone_number, query=query
        )
        db.session.add(contact)
        db.session.commit()

        flash(Markup("Query submitted successfully!"), "success")
        return redirect(url_for("contact_us"))

    return render_template("contact_us.html")


def save_contact(lead_name, service, phone_number, query):
    if Users.query.filter_by(phone_number=phone_number).first():
        flash("Phone number already exists.", "error")
        return False

    contact = Users(
        lead_name=lead_name, service=service, phone_number=phone_number, query=query
    )
    db.session.add(contact)
    db.session.commit()
    return True


@app.route("/login/manager", methods=["GET", "POST"])
def manager():
    if session.get("user_option") == "manager":
        return render_template(
            "manager.html",
        )
        total_users = Users.query.count()
    flash("Access denied. Admins only.", "error")
    return redirect(url_for("login"))


@app.route("/dashboard")
def manager_dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run()
