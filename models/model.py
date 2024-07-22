from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# Employee model for "employees" table
class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    lead_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    option = db.Column(db.String, nullable=False)

    def __init__(self, lead_name, email, phone_number, password, option):
        self.lead_name = lead_name
        self.email = email
        self.phone_number = phone_number
        self.password = generate_password_hash(password)
        self.option = option


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    lead_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    option = db.Column(db.String, nullable=False, default="user")

    def __init__(self, lead_name, email, phone_number, password):
        self.lead_name = lead_name
        self.email = email
        self.phone_number = phone_number
        self.password = generate_password_hash(password)  # Hash the password


# Query model for "query" table
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
