from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, FileField,BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.fields import DateField # ✅ add this
from wtforms.validators import DataRequired, Optional

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    role = SelectField("Role", choices=[("seeker", "Job Seeker"), ("employer", "Employer")], validators=[DataRequired()])
    company = StringField("Company")  # optional for seekers
    skills = StringField("Skills")
    industry = StringField("Industry")
    submit = SubmitField("Register")




class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")



class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Sign In")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")   # 👈 add this
    submit = SubmitField("Sign In")


class JobForm(FlaskForm):
    title = StringField("Job Title", validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField("Description", validators=[DataRequired()])
    qualifications = TextAreaField("Qualifications", validators=[Optional()])
    responsibilities = TextAreaField("Responsibilities", validators=[Optional()])
    location = StringField("Location", validators=[Optional()])
    job_type = SelectField("Job Type", choices=[("Full-time","Full-time"),("Part-time","Part-time"),("Contract","Contract"),("Remote","Remote")], validators=[Optional()])
    salary_min = IntegerField("Salary Min", validators=[Optional(), NumberRange(min=0)])
    salary_max = IntegerField("Salary Max", validators=[Optional(), NumberRange(min=0)])

class ProfileForm(FlaskForm):
    # Common fields
    name = StringField("Full Name", validators=[DataRequired()])
    phone = StringField("Phone Number", validators=[Optional()])
    education = StringField("Education", validators=[Optional()])
    #professional = StringField("Professional Experience", validators=[Optional()])
    birthday = DateField("Birthday", format="%Y-%m-%d", validators=[Optional()])
    nationality = StringField("Nationality", validators=[Optional()])

    # Documents
    other_docs = FileField("Other Documents", validators=[Optional()])
    resume = FileField("Resume", validators=[Optional()])  # seeker only

    # Employer-specific fields
    company_name = StringField("Company Name", validators=[Optional()])
    company_contact = StringField("Company Contact Details", validators=[Optional()])
    employee_id = StringField("Employee ID", validators=[Optional()])
    department = StringField("Department", validators=[Optional()])
    designation = StringField("Designation", validators=[Optional()])
    reporting_to = StringField("Reporting To", validators=[Optional()])
    joined_on = DateField("Joined On", format="%Y-%m-%d", validators=[Optional()])
    status = StringField("Status", validators=[Optional()])
    notice_period = StringField("Notice Period", validators=[Optional()])
    
    degree = StringField("Degree", validators=[DataRequired()]) 
    institution = StringField("Institution", validators=[DataRequired()]) 
    graduation_year = IntegerField("Graduation Year") 
    major = StringField("Major")
    
    current_position = StringField("Current Position", validators=[DataRequired()]) 
    company = StringField("Company", validators=[DataRequired()]) 
    experience_years = IntegerField("Years of Experience") 
    skills = StringField("Skills")

    submit = SubmitField("Save Changes")



class ApplicationForm(FlaskForm):
    cover_letter = TextAreaField("Cover Letter", validators=[Optional(), Length(max=5000)])
