from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from sqlalchemy import func
from markupsafe import Markup

from route import simple_page

from werkzeug.security import generate_password_hash, check_password_hash

from models.model import Employee, User, Query, db


app = Flask(__name__)
app.register_blueprint(simple_page)


bootstrap = Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///salon.db"
app.config["SECRET_KEY"] = "abczyx"  # Secret key for session management

db.init_app(app)

migrate = Migrate(app, db)


# Function to save employee data to database
def save_employee(lead_name, email, phone_number, password):
    if Employee.query.filter_by(email=email).first():
        flash("Email already exists.", "error")
        return False

    employee = Employee(
        lead_name=lead_name,
        email=email,
        phone_number=phone_number,
        password=generate_password_hash(password),
        option="employee",
    )
    db.session.add(employee)
    db.session.commit()
    return True


# Migrate users to employees database
def migrate_users():
    with app.app_context():
        options = ["admin", "manager"]
        for option in options:
            users = User.query.filter(User.option == option).all()
            for user in users:
                new_user = Employee(
                    lead_name=user.lead_name,
                    email=user.email,
                    phone_number=user.phone_number,
                    password=user.password,
                    option=user.option,
                )
                db.session.add(new_user)
                db.session.delete(user)
            db.session.commit()


# Migrate employees to users database
def migrate_employee():
    with app.app_context():
        options_user = ["user"]
        for option in options_user:
            employees = Employee.query.filter(Employee.option == option).all()
            for employee in employees:
                new_emp = User(
                    lead_name=employee.lead_name,
                    email=employee.email,
                    phone_number=employee.phone_number,
                    password=employee.password,
                )
                db.session.add(new_emp)
                db.session.delete(employee)
            db.session.commit()


# Function to save user data to database
def save_user(lead_name, email, phone_number, password):
    if User.query.filter_by(email=email).first():
        flash("Email already exists.", "error")
        return False

    if email.endswith("@admin.com"):
        employee = Employee(
            lead_name=lead_name,
            email=email,
            phone_number=phone_number,
            password=password,
            option="admin",
        )
        db.session.add(employee)
        db.session.commit()
        return True

    elif email.endswith("@manager.com"):
        employee = Employee(
            lead_name=lead_name,
            email=email,
            phone_number=phone_number,
            password=password,
            option="manager",
        )
        db.session.add(employee)
        db.session.commit()
        return True

    else:
        # Create new User object and add to session
        user = User(
            lead_name=lead_name,
            email=email,
            phone_number=phone_number,
            password=password,
        )
        db.session.add(user)
        db.session.commit()
        return True


def check_user(email, password):
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return user.lead_name, user.option
    employee = Employee.query.filter_by(email=email, password=password).first()
    if employee:
        return employee.lead_name, employee.option
    return None, None


# Function to control caching behavior
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# Function for home page
def hello_world():
    return render_template("home.html")


# Function for signup
def signup():
    if request.method == "POST":
        lead_name = request.form["lead_name"]
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        password = request.form["password"]

        existing_user = (
            db.session.query(User)
            .filter_by(phone_number=phone_number, email=email)
            .first()
        )

        existing_emp = db.session.query(Employee).filter_by(email=email).first()

        existing_employee = (
            db.session.query(Query).filter_by(phone_number=phone_number).first()
        )

        existing_query = (
            db.session.query(Query)
            .filter_by(lead_name=lead_name, phone_number=phone_number)
            .first()
        )

        if existing_emp:
            flash("Email or phone number already exists!", "error")
            return redirect(url_for("simple_page.create_account"))
        if existing_user:
            flash("Email or phone number already exists!", "error")
            return redirect(url_for("simple_page.create_account"))

        if existing_employee and existing_employee.lead_name != lead_name:
            flash("Lead name already exists for this phone number!", "error")
            return redirect(url_for("simple_page.create_account"))

        if not (8 <= len(password) <= 13):
            flash("Password must be between 8 to 13 characters!", "error")
            return redirect(url_for("simple_page.create_account"))

        else:
            if existing_query:
                save_user(lead_name, email, phone_number, password)
                flash(
                    Markup(
                        'Account created! <a href="/login" style="color:green">Login</a> now'
                    ),
                    "success",
                )
                return redirect(url_for("simple_page.create_account"))

            if save_user(lead_name, email, phone_number, password):
                flash(
                    Markup(
                        'Account created! <a href="/login" style="color:green">Login</a> now'
                    ),
                    "success",
                )
                return redirect(url_for("simple_page.create_account"))

    return render_template("signup.html")


# Function for login
def login():
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        user = (
            User.query.filter_by(email=email).first()
            or Employee.query.filter_by(email=email).first()
        )
        if user and check_password_hash(user.password, password):
            session.update(
                {
                    "lead_name": user.lead_name,
                    "email": email,
                    "user_option": user.option,
                }
            )
            if user.option == "user":
                session["phone_number"] = user.phone_number
                return redirect(url_for("simple_page.login_user_details"))
            else:
                return redirect(
                    url_for(
                        "simple_page.admin_login"
                        if user.option == "admin"
                        else "simple_page.manager_login"
                    )
                )
        else:
            flash(
                Markup(
                    'Email or password incorrect! <a href="/signup" style="color:green"> Signup </a>instead'
                ),
                "success",
            )
    return render_template("/login/login.html")


# Function for contact us
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
                return redirect(url_for("simple_page.contact_form"))
    return render_template("/contact_us/contact_us.html")


# Function for login user
def login_user():
    if session.get("user_option") == "user":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        status = session.get("status")
        id = session.get("id")
        user = User.query.filter_by(lead_name=lead_name).first()
        return render_template(
            "/login/login_user.html",
            lead_name=lead_name,
            status=status,
            id=id,
            phone_number=phone_number,
        )
    return redirect(url_for("simple_page.home"))


# Function for user details user
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
                    "/login/login_user.html",
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
                    "/login/login_user.html",
                    lead_name=lead_name,
                    status=status,
                    id=id,
                    phone_number=phone_number,
                )
        else:
            return redirect(url_for("simple_page.home"))
    else:
        return redirect(url_for("simple_page.home"))


# Function for contact us for signed up
def contact_us_for_signedup():
    lead_name = session.get("lead_name")
    phone_number = session.get("phone_number")

    if not lead_name or not phone_number:
        return redirect(url_for("simple_page.home"))

    if request.method == "GET":
        return render_template(
            "/contact_us/contact_us_for_signed.html",
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
                return redirect(url_for("simple_page.login_user_details"))

    return render_template("/login/login_user.html")


# Function for admin's login
def login_admin():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        total_users_registered = db.session.query(User).filter_by(option="user").count()
        total_employees = db.session.query(Employee).count()

        return render_template(
            "/admin/admin.html",
            lead_name=lead_name,
            phone_number=phone_number,
            total_users_registered=total_users_registered,
            total_employees=total_employees,
        )
    return redirect(url_for("simple_page.home"))


# Function to display employees for admin
def login_admin_employees():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")

        page = request.args.get("page", 1, type=int)
        per_page = 10

        employees = Employee.query.paginate(page=page, per_page=per_page)

        emp_total = db.session.query(Employee).all()
        return render_template(
            "/admin/admin_employee_page.html",
            lead_name=lead_name,
            phone_number=phone_number,
            employees=employees,
            page=page,
            per_page=per_page,
            emp_total=emp_total,
        )
    return redirect(url_for("simple_page.home"))


# Function to display users for admin
def login_admin_users():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")

        page_2 = request.args.get("page_2", 1, type=int)
        per_page_2 = 10

        users = User.query.paginate(page=page_2, per_page=per_page_2)

        users_total = db.session.query(User).all()
        return render_template(
            "/admin/admin_user_page.html",
            lead_name=lead_name,
            phone_number=phone_number,
            page_2=page_2,
            per_page_2=per_page_2,
            users=users,
            users_total=users_total,
        )
    # return redirect(url_for("simple_page.home"))
    return redirect(url_for("home"))

    
"""
def login_admin_users():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")

        page = request.args.get("page", 1, type=int)
        per_page = 10

        users = User.query.paginate(page=page, per_page=per_page)

        users_total = db.session.query(User).count()
        return render_template(
            "/admin/admin_user_page.html",
            lead_name=lead_name,
            phone_number=phone_number,
            page=page,
            per_page=per_page,
            users=users,
            users_total=users_total,
        )
    return redirect(url_for("simple_page.home"))
"""

# Function to display flash message
def all_employees():
    if session.get("user_option") == "admin":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        return render_template(
            "/admin/all_employees.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("simple_page.home"))


# Function to add new user
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

            if option != "user" and (
                db.session.query(User).filter_by(email=email).first()
                or db.session.query(User).filter_by(phone_number=phone_number).first()
                or db.session.query(Employee)
                .filter_by(phone_number=phone_number)
                .first()
                or db.session.query(Employee).filter_by(email=email).first()
                or db.session.query(Query).filter_by(phone_number=phone_number).first()
            ):
                flash("User with this email or phone number already exists.")
                return render_template("/admin/admin_add.html")

            if not lead_name or not email or not password:
                flash("Enter all details to proceed.")
                return render_template("/admin/admin_add.html")

            if not len(lead_name) < 28:
                flash("Not more than 28 characters are allowed!", "error")
                return redirect(url_for("simple_page.flash_message"))

            if not phone_number.isdigit() or len(phone_number) != 10:
                flash("Please enter a valid 10-digit phone number")
                return redirect(url_for("simple_page.flash_message"))

            if option == "user" and not email.endswith("@gmail.com"):
                flash("Enter correct mail to proceed.")
                return render_template("/admin/admin_add.html")

            if option == "admin" and not email.endswith("@admin.com"):
                flash("Enter correct mail to proceed.")
                return render_template("/admin/admin_add.html")

            if option == "manager" and not email.endswith("@manager.com"):
                flash("Enter correct mail to proceed.")
                return render_template("/admin/admin_add.html")

            existing_user_mail = db.session.query(User).filter_by(email=email).first()
            if existing_user_mail:
                flash("Email or phone number already exists!", "error")
                return redirect(url_for("simple_page.flash_message"))
            existing_user = (
                db.session.query(User).filter_by(phone_number=phone_number).first()
            )
            if existing_user:
                flash("Email or phone number already exists!", "error")
                return redirect(url_for("simple_page.flash_message"))

            try:
                if option == "user":
                    user = User(
                        lead_name=lead_name,
                        email=email,
                        phone_number=phone_number,
                        password=password,
                    )
                    db.session.add(user)
                    flash("User added successfully.")
                else:
                    contact = Employee(
                        lead_name=lead_name,
                        email=email,
                        phone_number=phone_number,
                        password=password,
                        option=option,
                    )
                    db.session.add(contact)
                    flash("Employee added successfully.")
                db.session.commit()
                return redirect(url_for("simple_page.flash_message"))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}")
                return render_template("/admin/admin_add.html")

    return render_template("/admin/admin_add.html")


# Function for updating employee
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
                return render_template("/admin/all_employees.html")

            if not len(lead_name) < 28:
                flash("Not more than 28 characters are allowed!", "error")
                return redirect(url_for("simple_page.flash_message"))

            if option == "admin" and not email.endswith("@admin.com"):
                flash("Enter correct email.", "error")
                return redirect(url_for("simple_page.flash_message"))

            if option == "manager" and not email.endswith("@manager.com"):
                flash("Enter correct email.", "error")
                return redirect(url_for("simple_page.flash_message"))

            if not phone_number.isdigit() or len(phone_number) != 10:
                flash("Please enter a valid 10-digit phone number")
                return redirect(url_for("simple_page.flash_message"))

            queries = (
                db.session.query(Query).filter_by(phone_number=phone_number).first()
            )

            if queries and queries.phone_number == phone_number:
                flash("Phone number already exists!", "error")
                return redirect(url_for("simple_page.flash_message"))

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
                return redirect(url_for("simple_page.flash_message"))
            else:
                if id == "":
                    flash("Please enter the employee's ID.", "error")
                    return redirect(url_for("simple_page.flash_message"))
                else:
                    flash("No employee found with the provided ID.", "error")
                    return redirect(url_for("simple_page.flash_message"))
        id = request.args.get("id")
        if id:
            employee = db.session.query(Employee).filter_by(id=id).first()
            if employee:
                return render_template("/admin/admin_employee_page.html")
            else:
                flash("No employee found with the provided ID.", "error")
                return render_template("/admin/admin_employee_page.html")
    return redirect(url_for("simple_page.home"))


# Function for updating user by admin
def employees_update_users():
    if session.get("user_option") == "admin":
        if request.method == "POST":
            id = request.form.get("id")
            phone_number = request.form.get("phone_number")
            email = request.form.get("email")
            lead_name = request.form.get("lead_name")
            option = request.form.get("option")

            if not email and not lead_name and not option and not phone_number:
                flash("Enter at least one field to proceed further.", "error")
                return redirect(url_for("simple_page.update_an_user"))

            if not len(lead_name) < 28:
                flash("Not more than 28 characters are allowed!", "error")
                return redirect(url_for("simple_page.flash_message"))

            if option == "admin" and not email.endswith("@admin.com"):
                flash("Enter correct email.", "error")
                return redirect(url_for("simple_page.flash_message"))

            if option == "manager" and not email.endswith("@manager.com"):
                flash("Enter correct email.", "error")
                return redirect(url_for("simple_page.flash_message"))

            if not phone_number.isdigit() or len(phone_number) != 10:
                flash("Please enter a valid 10-digit phone number")
                return redirect(url_for("simple_page.flash_message"))

            queries = (
                db.session.query(Query).filter_by(phone_number=phone_number).first()
            )

            if queries and queries.phone_number == phone_number:
                flash("Phone number already exists!", "error")
                return redirect(url_for("simple_page.flash_message"))

            employee = (
                db.session.query(Employee).filter_by(phone_number=phone_number).first()
            )
            if employee and employee.phone_number == phone_number:
                flash("Phone number already exists!", "error")
                return redirect(url_for("simple_page.flash_message"))

            employee_mail = db.session.query(Employee).filter_by(email=email).first()
            if employee_mail and employee_mail.email == email:
                flash("Email already exists!", "error")
                return redirect(url_for("simple_page.flash_message"))

            user = db.session.query(User).filter_by(id=id).first()

            if user:
                if email:
                    user.email = email
                if lead_name:
                    user.lead_name = lead_name
                if phone_number:
                    user.phone_number = phone_number
                if option:
                    user.option = option

                db.session.commit()
                flash("User updated successfully.", "success")
                return redirect(url_for("simple_page.flash_message"))
            else:
                flash("No user found with the provided ID.", "error")
                return redirect(url_for("simple_page.flash_message"))

        id = request.args.get("id")
        if id:
            user = db.session.query(User).filter_by(id=id).first()
            if user:
                return render_template("simple_page.update_user.html", user=user)
            else:
                flash("No user found with the provided ID.", "error")
                return redirect(url_for("simple_page.flash_message"))

        return render_template("/admin/admin.html")
    return redirect(url_for("simple_page.home"))


# Function for deleting employee by admin
def employee_delete():
    if session.get("user_option") == "admin":
        id = request.args.get("id")

        employee = db.session.query(Employee).filter_by(id=id).first()
        if employee:
            db.session.delete(employee)
            db.session.commit()
            flash("Employee deleted successfully.", "success")
        else:
            flash("Employee not found.", "error")

        return redirect(url_for("simple_page.flash_message"))
    return redirect(url_for("simple_page.home"))


# Function for deleting user by admin
def users_delete():
    if session.get("user_option") == "admin":
        id = request.args.get("id")
        user = db.session.query(User).filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully.", "success")
        else:
            flash("User not found.", "error")

        return redirect(url_for("simple_page.flash_message"))
    return redirect(url_for("simple_page.home"))


# Function for login manager
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
            "/manager/manager.html",
            total_users=total_users,
            pending_leads=pending_leads,
            call_done_leads=call_done_leads,
            waiting_leads=waiting_leads,
            scheduled_leads=scheduled_leads,
            converted_leads=converted_leads,
            declined_leads=declined_leads,
        )
    return redirect(url_for("simple_page.home"))


# Function to display flash message
def all_leads():
    if session.get("user_option") == "manager":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        return render_template(
            "/manager/all_leads.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("simple_page.home"))


# Function to add new lead by manager
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
                        "simple_page.add_leads",
                        lead_name=lead_name,
                        phone_number=phone_number,
                    )
                )
            if db.session.query(Query).filter_by(phone_number=phone_number).first():
                flash("Phone number already exists.")
                return redirect(
                    url_for(
                        "simple_page.add_leads",
                        lead_name=lead_name,
                        phone_number=phone_number,
                    )
                )
            if db.session.query(User).filter_by(phone_number=phone_number).first():
                flash("Phone number already exists.")
                return redirect(
                    url_for(
                        "simple_page.add_leads",
                        lead_name=lead_name,
                        phone_number=phone_number,
                    )
                )
            if db.session.query(Employee).filter_by(phone_number=phone_number).first():
                flash("Phone number already exists.")
                return redirect(
                    url_for(
                        "simple_page.add_leads",
                        lead_name=lead_name,
                        phone_number=phone_number,
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
                    flash("Query added successfully.")
                    return redirect(
                        url_for(
                            "simple_page.flash_message_manager",
                            lead_name=lead_name,
                            phone_number=phone_number,
                        )
                    )
                except:
                    db.session.rollback()
                    flash("Phone number already exists.")
                    return render_template(
                        "/manager/manager_add.html",
                        lead_name=lead_name,
                        phone_number=phone_number,
                    )
        return render_template(
            "/manager/manager_add.html", lead_name=lead_name, phone_number=phone_number
        )
    return redirect(url_for("simple_page.home"))


# Function to update lead by manager
def all_leads_update():
    if session.get("user_option") == "manager":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        query = session.get("query")
        if request.method == "POST":
            id = request.form.get("id")
            lead_name = request.form.get("lead_name")
            services = request.form.getlist("service")
            service = ", ".join(services)
            query = request.form.get("query")
            status = request.form.get("status")
            if not id:
                flash("Enter ID to proceed further.", "error")
                return render_template(
                    "/manager/manager_update.html",
                    lead_name=lead_name,
                    phone_number=phone_number,
                )
            if not lead_name and not service and not status and not query:
                flash("Enter at least one field to proceed further.", "error")
                return render_template(
                    "/manager/manager_update.html",
                    lead_name=lead_name,
                    phone_number=phone_number,
                )
            else:
                lead = db.session.query(Query).filter_by(id=id).first()
                if lead:
                    if lead_name:
                        lead.lead_name = lead_name
                    if service:
                        lead.service = service
                    if query:
                        lead.query = query
                    if status:
                        lead.status = status
                    db.session.commit()
                    flash("Query updated successfully.", "success")
                    return redirect(url_for("flash_message_manager"))
                else:
                    flash("No lead found with the above ID.", "error")
                    return render_template("/manager/manager_update.html")
        return render_template(
            "/manager/manager_update.html",
            lead_name=lead_name,
            phone_number=phone_number,
        )
    return redirect(url_for("simple_page.home"))


# Function to delete lead by manager
def all_leads_delete():
    if session.get("user_option") == "manager":
        id = request.args.get("id")
        query = db.session.query(Query).filter_by(id=id).first()
        if query:
            db.session.delete(query)
            db.session.commit()
            flash("Query deleted successfully.", "success")
        else:
            flash("Query not found.", "error")

        return render_template(
            "all_leads.html",
        )
    return redirect(url_for("simple_page.home"))


# Function to display all  queries
def all_queries():
    if session.get("user_option") == "manager":
        if request.method == "POST":
            id = request.form.get("id")
            lead_name = request.form.get("lead_name")
            services = request.form.getlist("service")
            service = ", ".join(services)
            phone_number = request.form.get("phone_number")
            query = request.form.get("query")
            status = request.form.get("status")

            queries = db.session.query(Query).filter_by(id=id).first()

            if queries:
                queries.lead_name = lead_name
                queries.service = service
                queries.phone_number = phone_number
                queries.query = query
                queries.status = status

                db.session.commit()
                flash("Query updated successfully.", "success")
            else:
                flash("Query not found.", "error")

            return redirect(url_for("simple_page.view_all_queries"))

        queries = db.session.query(Query).all()
        return render_template(
            "/manager/all_queries.html",
            queries=queries,
        )
    return redirect(url_for("simple_page.home"))


# Function for reset
def reset():
    if session.get("user_option") == "user":
        lead_name = session.get("lead_name")
        phone_number = session.get("phone_number")
        email = session.get("email")
        if request.method == "POST":
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            user = db.session.query(User).filter_by(email=email).first()
            if not password or not confirm_password:
                flash("Please fill all the fields.", "error")
                return render_template(
                    "/login/login_user.html",
                    lead_name=lead_name,
                    phone_number=phone_number,
                )
            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template(
                    "/login/login_user.html",
                    lead_name=lead_name,
                    phone_number=phone_number,
                )
            else:
                if len(password) >= 8 and len(password) < 13:
                    user.password = generate_password_hash(confirm_password)
                    db.session.commit()
                    flash("Password reset successfully.", "success")
                    return render_template(
                        "login/login_user.html",
                        lead_name=lead_name,
                        phone_number=phone_number,
                    )
                else:
                    flash("Password must be atleast 8 characters long.", "error")
                    return render_template(
                        "/login/login_user.html",
                        lead_name=lead_name,
                        phone_number=phone_number,
                    )

    return redirect(url_for("simple_page.home"))


# Function for forgot password
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        lead_name = request.form.get("lead_name")
        phone_number = request.form.get("phone_number")
        if not email or not lead_name or not phone_number:
            flash("Please fill all the fields.", "error")
            return render_template("/login/login.html")
        user = db.session.query(User).filter_by(email=email).first()
        if user is None:
            flash("User with this email does not exist.", "error")
            return render_template("/login/login.html")
        else:
            flash(
                "Password reset instructions have been sent to your email.", "success"
            )
            return render_template("/login/login.html")


# Function to logout
def logout():
    session.clear()
    return render_template("logout.html")


# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        migrate_employee()
        migrate_users()
        app.run()
