from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from extensions import db,bcrypt  # adjust import to match your project
from werkzeug.security import generate_password_hash, check_password_hash


#db = SQLAlchemy()

class User(UserMixin, db.Model):   # 👈 inherit UserMixin for Flask-Login
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20))   # "seeker" or "employer"
    


  

    # ✅ Password methods using Werkzeug
    def set_password(self, password):
        """Hash and store the user's password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)


    # Seeker-specific
    skills = db.Column(db.String(200))
    resume_path = db.Column(db.String(200))
    other_docs_path = db.Column(db.String(200))
    

    # Employer-specific
    company = db.Column(db.String(200))
    industry = db.Column(db.String(200))
    logo_path = db.Column(db.String(200))

    # Common profile fields
    education = db.Column(db.String(200))   # e.g. "B.Tech in Computer Science"
    professional = db.Column(db.String(200))        # work experience details
    other_docs_path = db.Column(db.String(200)) # file path for other documents
    avatar_url = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    birthday = db.Column(db.Date)
    nationality = db.Column(db.String(50))

    
    # Employer-specific fields
    company_name = db.Column(db.String(100))
    company_contact = db.Column(db.String(100))
    employee_id = db.Column(db.String(50))
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    reporting_to = db.Column(db.String(100))
    joined_on = db.Column(db.Date)
    status = db.Column(db.String(50))
    notice_period = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    # Relationships
    jobs = db.relationship("Job", back_populates="employer", lazy=True)
    applications = db.relationship("Application", back_populates="seeker", lazy=True)


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    qualifications = db.Column(db.Text)
    responsibilities = db.Column(db.Text)
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    summary = db.Column(db.Text) 
    details = db.Column(db.Text)

    # Relationships
    employer = db.relationship("User", back_populates="jobs")
    applications = db.relationship("Application", back_populates="job", lazy=True)


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    seeker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    cover_letter = db.Column(db.Text)
    resume_url = db.Column(db.String(200))
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    seeker = db.relationship("User", back_populates="applications")
    job = db.relationship("Job", back_populates="applications")
