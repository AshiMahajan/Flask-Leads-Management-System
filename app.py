from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
)
from sqlalchemy import func
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///salon.db"
app.config["SECRET_KEY"] = "abczyx"  # Secret key for session management

db = SQLAlchemy(app)


# Employee model for employees table
class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    lead_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    option = db.Column(db.String, nullable=False)

    # Constructor (__init__) for Employee class
    def __init__(self, lead_name, email, phone_number, password, option):
        self.lead_name = lead_name  # Initialize lead_name attribute
        self.email = email  # Initialize email attribute
        self.phone_number = phone_number  # Initialize phone_number attribute
        self.password = password  # Initialize password attribute
        self.option = option  # Initialize option attribute


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    lead_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    option = db.Column(db.String, nullable=False)

    def __init__(self, lead_name, email, phone_number, password, option):
        self.lead_name = lead_name
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.option = option


class Query(db.Model):
    __tablename__ = "user_queries"
    id = db.Column(db.Integer, primary_key=True)
    lead_name = db.Column(db.String, nullable=False)
    service = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    query = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default="pending")

    def __init__(self, lead_name, service, phone_number, query):
        self.lead_name = lead_name
        self.service = service
        self.phone_number = phone_number
        self.query = query


# Function to save employee data to database
def save_employee(lead_name, email, phone_number, password, option):

    # Check if email already exists in employees table
    if Employee.query.filter_by(email=email).first():
        flash("Email already exists.", "error")
        return False

    # Create new Employee object and add to session
    employee = Employee(
        lead_name=lead_name,
        email=email,
        phone_number=phone_number,
        password=password,
        option=option,
    )
    db.session.add(employee)  # Add employee to session
    db.session.commit()  # Commit changes to database
    return True


# Function to save user data to database
def save_user(lead_name, email, phone_number, password, option):

    # Check if email already exists in users table
    if User.query.filter_by(email=email).first():
        flash("Email already exists.", "error")
        return False

    # Create new User object and add to session
    user = User(
        lead_name=lead_name,
        email=email,
        phone_number=phone_number,
        password=password,
        option=option,
    )
    db.session.add(user)  # Add employee to session
    db.session.commit()  # Commit changes to database
    return True


# Function to check user credentials
def check_user(email, password):
    # Check if user exists in users table
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return user.lead_name, user.option  # Return lead_name and option
    # Check if user exists in employees table
    employee = Employee.query.filter_by(email=email, password=password).first()
    if employee:
        return employee.lead_name, employee.option  # Return lead_name and option
    return None, None  # Return None if user not found


# Route for home page
@app.route("/")
def hello_world():
    return render_template("home.html")


# Route for signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        lead_name = request.form["lead_name"]
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        password = request.form["password"]
        option = request.form["options"]

        existing_user = db.session.query(User).filter_by(email=email).first()
        existing_employee = (
            db.session.query(Query).filter_by(phone_number=phone_number).first()
        )

        if existing_user or existing_employee:
            flash("Email or phone number already exists!", "error")
        else:
            if (
                (option == "admin" and not email.endswith("@marvel.com"))
                or (option == "user" and email.endswith("@marvel.com"))
                or (option == "manager" and not email.endswith("@manager.com"))
                or (option == "user" and email.endswith("@manager.com"))
            ):
                flash(f"Invalid email for {option} option!", "error")
            elif not (8 <= len(password) <= 13):
                flash("Password must be between 8 to 13 characters!", "error")
            elif option == "user":
                save_user(lead_name, email, phone_number, password, option)
                flash(
                    Markup(
                        'Account created! <a href="/login" style="color:green">Login</a> now'
                    ),
                    "success",
                )
                return redirect(url_for("signup"))
            else:
                if save_employee(lead_name, email, phone_number, password, option):
                    flash(
                        Markup(
                            'Account created! <a href="/login" style="color:green">Login</a> now'
                        ),
                        "success",
                    )
                    return redirect(url_for("signup"))

        return render_template(
            "signup.html",
            lead_name=lead_name,
            email=email,
            phone_number=phone_number,
            option=option,
        )

    return render_template("signup.html")


# Route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        lead_name, user_option = check_user(email, password)
        if user_option:
            session.update(
                {"lead_name": lead_name, "email": email, "user_option": user_option}
            )
            if user_option == "user":
                user = User.query.filter_by(email=email).first()
                session["phone_number"] = user.phone_number
                return redirect(url_for("login_user"))
            else:
                return redirect(
                    url_for(
                        "login_admin" if user_option == "admin" else "login_manager"
                    )
                )
        else:
            flash(
                Markup(
                    'Email or password incorrect! <a href="/signup" style="color:green"> Signup </a>instead'
                ),
                "success",
            )
    return render_template("login.html")


# Route for contact us after logging in
@app.route("/login/user/contact_us", methods=["GET", "POST"])
def contact_us_for_signedup():
    lead_name = session.get("lead_name")
    phone_number = session.get("phone_number")

    if not lead_name or not phone_number:
        return redirect(url_for("hello_world"))

    if request.method == "GET":
        return render_template(
            "contact_us_for_signed.html",
            lead_name=lead_name,
            phone_number=phone_number,
        )

    if request.method == "POST":
        if session.get("user_option") == "user":
            services = request.form.getlist("service")
            service = ", ".join(services)
            query = request.form.get("query")
            status = request.form.get("status")
            if not service or not query:
                flash("Please fill out all fields.", "error")
            else:
                contact = Query(
                    lead_name=lead_name,
                    service=service,
                    phone_number=phone_number,
                    query=query,
                )
                db.session.add(contact)
                db.session.commit()
                flash(
                    Markup(
                        "<h1 style='color: green'>Query Submitted, we will reach out to you shortly!</h1>"
                    ),
                    "success",
                )
                return redirect(url_for("login_user"))

    return render_template("login_user.html")


# Route for contact us page
@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        lead_name = request.form.get("lead_name")
        services = request.form.getlist("service")
        service = ", ".join(services)
        phone_number = request.form.get("phone_number")
        query = request.form.get("query")

        if not lead_name or not service or not phone_number or not query:
            flash("Please fill out all fields.", "error")
        if len(phone_number) != 10:
            flash("Please enter the correct phone number.", "error")
        else:
            existing_query = (
                db.session.query(Query).filter_by(phone_number=phone_number).first()
            )
            if existing_query:
                flash("Phone number already exists.", "error")
            else:
                new_query = Query(lead_name, service, phone_number, query)
                db.session.add(new_query)
                db.session.commit()
                flash(
                    Markup(
                        "<h1 style= 'color: green'>Query Submitted, we will reach out to you shortly!</h1>"
                    ),
                    "success",
                )
                return redirect(url_for("contact_us"))
    return render_template("contact_us.html")


# Route for admin's dashboard page
@app.route("/login/admin", methods=["GET"])
def login_admin():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        employees = Employee.query.all()
        return render_template(
            "admin_page.html",
            lead_name=lead_name,
            phone_number=phone_number,
            employees=employees,
        )
    return redirect(url_for("hello_world"))


# Route for user's dashboard page
@app.route("/login/user", methods=["GET"])
def login_user():
    if session.get("user_option") == "user":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        status = session.get("status")
        id = session.get("id")
        user = User.query.filter_by(lead_name=lead_name).first()
        return render_template(
            "login_user.html",
            lead_name=lead_name,
            status=status,
            id=id,
            phone_number=phone_number,
        )
    return redirect(url_for("hello_world"))


# Route for manager's dashboard page
@app.route("/login/manager", methods=["GET", "POST"])
def login_manager():
    if session.get("user_option") == "manager":
        total_users = db.session.query(func.count(Query.id)).scalar()
        pending_leads = db.session.query(Query).filter_by(status="pending").count()
        call_done_leads = db.session.query(Query).filter_by(status="call_done").count()
        waiting_leads = db.session.query(Query).filter_by(status="waiting").count()
        scheduled_leads = db.session.query(Query).filter_by(status="scheduled").count()
        converted_leads = db.session.query(Query).filter_by(status="converted").count()
        declined_leads = db.session.query(Query).filter_by(status="declined").count()

        return render_template(
            "manager.html",
            total_users=total_users,
            pending_leads=pending_leads,
            call_done_leads=call_done_leads,
            waiting_leads=waiting_leads,
            scheduled_leads=scheduled_leads,
            converted_leads=converted_leads,
            declined_leads=declined_leads,
        )
    return redirect(url_for("hello_world"))


# Route for manager's add/ update/ delete page
@app.route("/manager/all_leads")
def all_leads():
    if session.get("user_option") == "manager":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        return render_template(
            "all_leads.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("hello_world"))


# Route for admin's add/ update/ delete page
@app.route("/admin/all_employees")
def all_employees():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        return render_template(
            "all_employees.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("hello_world"))


# Route for manager's add page
@app.route("/manager/all_leads/add", methods=["GET", "POST"])
def all_leads_add():
    if session.get("user_option") == "manager":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        if request.method == "POST":
            lead_name = request.form.get("lead_name")
            services = request.form.getlist("service")
            service = ", ".join(services)
            phone_number = request.form.get("phone_number")
            query = request.form.get("query")
            if (
                len(phone_number) != 10
                or service == ""
                or len(query) < 5
                or len(query) > 50
            ):
                flash("Enter all details correctly to proceed.")
                return redirect(
                    url_for(
                        "all_leads_add", lead_name=lead_name, phone_number=phone_number
                    )
                )
            if db.session.query(Query).filter_by(phone_number=phone_number).first():
                flash("Lead with this phone number already exists.")
                return redirect(
                    url_for(
                        "all_leads_add", lead_name=lead_name, phone_number=phone_number
                    )
                )
            else:
                try:
                    contact = Query(
                        lead_name=lead_name,
                        service=service,
                        phone_number=phone_number,
                        query=query,
                    )
                    db.session.add(contact)
                    db.session.commit()
                    flash("User added successfully.")
                    return redirect(
                        url_for(
                            "all_leads", lead_name=lead_name, phone_number=phone_number
                        )
                    )
                except:
                    db.session.rollback()
                    flash("Lead with this phone number already exists.")
                    return render_template(
                        "manager_add.html",
                        lead_name=lead_name,
                        phone_number=phone_number,
                    )
        return render_template(
            "manager_add.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("hello_world"))


# Route for manager's update page
@app.route("/manager/all_leads/update", methods=["GET", "POST"])
def all_leads_update():
    if session.get("user_option") == "manager":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        if request.method == "POST":
            id = request.form.get("id")
            services = request.form.getlist("service")
            service = ", ".join(services)
            query = request.form.get("query")
            status = request.form.get("status")
            if not id:
                flash("Enter ID to proceed further.", "error")
                return render_template(
                    "manager_update.html",
                    lead_name=lead_name,
                    phone_number=phone_number,
                )
            if not service and not status and not query:
                flash("Enter at least one field to proceed further.", "error")
                return render_template(
                    "manager_update.html",
                    lead_name=lead_name,
                    phone_number=phone_number,
                )
            else:
                lead = db.session.query(Query).filter_by(id=id).first()
                if lead:
                    # if phone_number:
                    #     lead.phone_number = phone_number
                    if service:
                        lead.service = service
                    if query:
                        lead.query = query
                    if status:
                        lead.status = status
                    db.session.commit()
                    flash("Lead updated successfully.", "success")
                    return redirect(url_for("all_leads"))
                else:
                    flash("No lead found with that phone number.", "error")
                    return render_template("manager_update.html")
        return render_template(
            "manager_update.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("hello_world"))


# Route for manager's delete page
@app.route("/manager/all_leads/delete", methods=["GET", "POST"])
def all_leads_delete():
    if session.get("user_option") == "manager":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        if request.method == "POST":
            id = request.form.get("id")
            if not id:
                flash("Please enter the lead's ID.", "error")
                return render_template("manager_delete.html")
            else:
                lead = db.session.query(Query).filter_by(id=id).first()
                if lead:
                    db.session.delete(lead)
                    db.session.commit()
                    flash("Lead deleted successfully.")
                    return redirect(url_for("all_leads"))
                else:
                    flash("No lead found with the above ID.", "error")
                    return render_template("manager_delete.html")
        return render_template(
            "manager_delete.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("hello_world"))


# Route for user's tracking details (after logging-in)
@app.route("/your_details", methods=["GET", "POST"])
def your_details():
    if session.get("user_option") == "user":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        status = session.get("status")
        id = session.get("id")
    if "email" in session:
        user_email = session["email"]
        if request.method == "GET":
            status = session.get("status")

        user = db.session.query(User).filter_by(email=user_email).first()

        if user:
            user_query = (
                db.session.query(Query)
                .filter_by(phone_number=user.phone_number)
                .first()
            )

            if not user_query:
                flash(
                    "Please fill the 'Contact Us' first to track your query!",
                    "error",
                )
                return render_template(
                    "login_user.html",
                    lead_name=lead_name,
                    status=status,
                    id=id,
                    phone_number=phone_number,
                )
            else:
                flash(
                    Markup(
                        f"Status <br> '<span style = 'color: green'>{user_query.status}</span>'. <br> Your Query <br> '<span style = 'color: green'>{user_query.query}<span>'"
                    )
                )
                return render_template(
                    "login_user.html",
                    lead_name=lead_name,
                    status=status,
                    id=id,
                    phone_number=phone_number,
                )
        else:
            return redirect(url_for("hello_world"))
    else:
        return redirect(url_for("hello_world"))


# Route for logout
@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")


# Route for manager's all queries
@app.route("/login/manager/all_queries")
def all_queries():
    if session.get("user_option") == "manager":
        queries = db.session.query(Query).all()
        return render_template("all_queries.html", queries=queries)
    return redirect(url_for("hello_world"))


# Route for admin's add page
@app.route("/admin/add", methods=["GET", "POST"])
def employees_add():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        if request.method == "POST":
            lead_name = request.form.get("lead_name")
            email = request.form.get("email")
            phone_number = request.form.get("phone_number")
            password = request.form.get("password")
            option = request.form.get("option")

            if option == "user" and email.endswith("@gmail.com"):
                if db.session.query(User).filter_by(email=email).first():
                    flash("User with this email already exists.")
                    return render_template("admin_add.html")
                if db.session.query(User).filter_by(phone_number=phone_number).first():
                    flash("User with this phone number already exists.")
                    return render_template("admin_add.html")
                if (
                    db.session.query(Employee)
                    .filter_by(phone_number=phone_number)
                    .first()
                ):
                    flash("User with this phone number already exists.")
                    return render_template("admin_add.html")
                try:
                    user = User(
                        lead_name=lead_name,
                        email=email,
                        phone_number=phone_number,
                        password=password,
                        option=option,
                    )
                    db.session.add(user)
                    db.session.commit()
                    flash("User added successfully.")
                    return redirect(url_for("all_employees"))
                except Exception as e:
                    db.session.rollback()
                    return render_template("admin_add.html")
            else:
                if (
                    len(phone_number) != 10
                    or not lead_name
                    or not email
                    or not password
                ):
                    flash("Enter correct details to proceed.")
                    return render_template("admin_add.html")

                if option == "admin" and not email.endswith("@marvel.com"):
                    flash("Incorrect email for admin.")
                    return render_template("admin_add.html")

                if (
                    db.session.query(Employee)
                    .filter_by(phone_number=phone_number)
                    .first()
                ):
                    flash("User with this phone number already exists.")
                    return render_template("admin_add.html")

                try:
                    contact = Employee(
                        lead_name=lead_name,
                        email=email,
                        phone_number=phone_number,
                        password=password,
                        option=option,
                    )
                    db.session.add(contact)
                    db.session.commit()
                    flash("User added successfully.")
                    return redirect(url_for("all_employees"))
                except Exception as e:
                    db.session.rollback()
                    flash(f"An error occurred: {str(e)}")
                    return render_template("admin_add.html")

        return render_template("admin_add.html")
    return redirect(url_for("hello_world"))


# Route for admin's update page
@app.route("/admin/update", methods=["GET", "POST"])
def employees_update():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        if request.method == "POST":
            id = request.form.get("id")
            phone_number = request.form.get("phone_number")
            email = request.form.get("email")
            lead_name = request.form.get("lead_name")
            option = request.form.get("option")

            if not email and not lead_name and not option and not phone_number:
                flash("Enter at least one field to proceed further.", "error")
                return render_template("update_employee.html")

            employee = db.session.query(Employee).filter_by(id=id).first()

            if employee:
                if id:
                    employee.id = id
                if email:
                    employee.email = email
                if lead_name:
                    employee.lead_name = lead_name
                if phone_number:
                    employee.phone_number = phone_number
                if option:
                    employee.option = option

                db.session.commit()
                flash("Employee updated successfully.", "success")
                return redirect(url_for("all_employees"))
            else:
                if id == "":
                    flash("Please enter the employee's ID.", "error")
                    return render_template("update_employee.html")
                else:
                    flash("No employee found with the provided ID.", "error")
                    return render_template("update_employee.html")

        return render_template(
            "update_employee.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("hello_world"))


# Route for admin's delete page
@app.route("/admin/delete", methods=["GET", "POST"])
def employee_delete():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        if request.method == "POST":
            id = request.form.get("id")
            if not id:
                flash("Please enter the employee's ID.", "error")
                return render_template("delete_admin.html")
            else:
                lead = db.session.query(Employee).filter_by(id=id).first()
                if lead:
                    db.session.delete(lead)
                    db.session.commit()
                    flash("Employee deleted successfully.")
                    return redirect(url_for("all_employees"))
                else:
                    flash("No employee found with the above ID.", "error")
                    return render_template("delete_admin.html")
        return render_template(
            "delete_admin.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("hello_world"))


# Error handler (404 not found)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run()
