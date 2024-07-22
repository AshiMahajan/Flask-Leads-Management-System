from flask import Flask
from flask import Blueprint

app = Flask(__name__)

simple_page = Blueprint("simple_page", __name__, template_folder="templates")


@simple_page.route("/")
def home():
    from app import hello_world

    return hello_world()


# Route for signup
@simple_page.route("/signup", methods=["GET", "POST"])
def create_account():
    from app import signup

    return signup()


# Route for login
@simple_page.route("/login", methods=["GET", "POST"])
def log_into_account():
    from app import login

    return login()


# Route for login user
@simple_page.route("/login/user", methods=["GET"])
def login_user_details():
    from app import login_user

    return login_user()


# Route for contact us
@simple_page.route("/contact_us", methods=["GET", "POST"])
def contact_form():
    from app import contact_us

    return contact_us()


# Route for user's tracking details (after logging-in)
@simple_page.route("/your_details", methods=["GET", "POST"])
def user_details():
    from app import your_details

    return your_details()


# Route for contact us after logging in
@simple_page.route("/login/user/contact_us", methods=["GET", "POST"])
def contact_us_form_after_login():
    from app import contact_us_for_signedup

    return contact_us_for_signedup()


# Route for admin login
@simple_page.route("/login/admin", methods=["GET"])
def admin_login():
    from app import login_admin

    return login_admin()


# Route for admin's employee dashboard page
@simple_page.route("/login/admin/employee", methods=["GET"])
def employees_display():
    from app import login_admin_employees

    return login_admin_employees()


# Route for admin's user dashboard page
@simple_page.route("/login/admin/users", methods=["GET"])
def users_display():
    from app import login_admin_users

    return login_admin_users()


# Route to display flashed message
@simple_page.route("/admin/all_employees")
def flash_message():
    from app import all_employees

    return all_employees()


# Route for admin's add page
@simple_page.route("/admin/add", methods=["GET", "POST"])
def add_new_user():
    from app import employees_add

    return employees_add()


# Route for admin's update page
@simple_page.route("/admin/update", methods=["GET", "POST"])
def update_an_employee():
    from app import employees_update

    return employees_update()


# Route for updating user
@simple_page.route("/admin/update/user", methods=["GET", "POST"])
def update_an_user():
    from app import employees_update_users

    return employees_update_users()


# Function for deleting employee
@simple_page.route("/admin/delete", methods=["GET"])
def delete_an_employee():
    from app import employee_delete

    return employee_delete()


# Function for deleting user
@simple_page.route("/admin/delete/user", methods=["GET"])
def delete_an_user():
    from app import users_delete

    return users_delete()


# Route for manager's dashboard page
@simple_page.route("/login/manager", methods=["GET", "POST"])
def manager_login():
    from app import login_manager

    return login_manager()


# Route for manager's add/ update/ delete page
@simple_page.route("/manager/all_leads")
def flash_message_manager():
    from app import all_leads

    return all_leads()


# Route for manager's add page
@simple_page.route("/manager/all_leads/add", methods=["GET", "POST"])
def add_leads():
    from app import all_leads_add

    return all_leads_add()


# Route for manager's update page
@simple_page.route("/manager/all_leads/update", methods=["GET", "POST"])
def update_leads():
    from app import all_leads_update

    return all_leads_update()


# Route for manager's delete
@simple_page.route("/manager/all_leads/delete", methods=["GET", "POST"])
def delete_leads():
    from app import all_leads_delete

    return all_leads_delete()


# Route to view all queries
@simple_page.route("/login/manager/all_queries", methods=["GET", "POST"])
def view_all_queries():
    from app import all_queries

    return all_queries()


@simple_page.route("/login/user/reset_pwd", methods=["GET", "POST"])
def reset_pwd():
    from app import reset

    return reset()


@simple_page.route("/login/forgot_password", methods=["GET", "POST"])
def forgot_pwd():
    from app import forgot_password

    return forgot_password()


@simple_page.errorhandler(404)
def page_error(e):
    from app import page_not_found

    return page_not_found(e)


# Route for logout
@simple_page.route("/logout")
def log():
    from app import logout

    return logout()
