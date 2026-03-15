import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.utils import secure_filename
from config import Config
from extensions import db,bcrypt
from models import User, Job, Application
from forms import RegisterForm, LoginForm, JobForm, ProfileForm, ApplicationForm
from flask_migrate import Migrate # 👈 import Migrate
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room
import random
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from forms import ForgotPasswordForm
from forms import ResetPasswordForm




ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__, template_folder="templates")
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
migrate = Migrate(app, db)





app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rohitbhosle300@gmail.com'
app.config['MAIL_PASSWORD'] = 'rxtchebimpoplzdu'  # use an app password, not your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)



socketio = SocketIO(app)

@app.route("/test_email")
def test_email():
    try:
        msg = Message("Hello from Flask",
                      recipients=["rohitbhosle300@gmail.com"])  # replace with your test email
        msg.body = "This is a test email sent from Flask-Mail using Gmail SMTP and App Password."
        mail.send(msg)
        return "✅ Test email sent successfully!"
    except Exception as e:
        return f"❌ Failed to send email: {e}"



# Dummy applications with chat threads
applications = [
    {
        "id": 1,
        "job_title": "Frontend Developer",
        "status": "applied",
        "messages": [
            {"sender": "Recruiter", "content": "We have received your application.", "timestamp": "2026-01-30"},
            {"sender": "HR Team", "content": "Your interview is scheduled for Feb 5th at 10 AM.", "timestamp": "2026-02-01"}
        ]
    },
    {
        "id": 2,
        "job_title": "Backend Developer",
        "status": "under review",
        "messages": [
            {"sender": "Recruiter", "content": "Your profile is being reviewed.", "timestamp": "2026-02-02"}
        ]
    }
]

def get_application(app_id):
    return next((a for a in applications if a["id"] == app_id), None)



@app.route("/messages/<int:app_id>/send", methods=["POST"])
@login_required
def send_message(app_id):
    application = get_application(app_id)
    if not application:
        return "Application not found", 404

    content = request.form.get("content")
    msg = {
        "sender": current_user.name,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    application["messages"].append(msg)

    # Broadcast new message to all clients in this application room
    socketio.emit("new_message", msg, room=f"app_{app_id}")
    return redirect(url_for("application_messages", app_id=app_id))




@app.route("/messages/<int:app_id>/update_status", methods=["POST"])
@login_required
def update_status(app_id):
    application = get_application(app_id)
    if not application:
        return "Application not found", 404

    new_status = request.form.get("status")
    application["status"] = new_status

    # Broadcast status update
    socketio.emit("status_update", {"status": new_status}, room=f"app_{app_id}")
    return redirect(url_for("application_messages", app_id=app_id))


@socketio.on("join")
def on_join(data):
    app_id = data["app_id"]
    join_room(f"app_{app_id}")



@app.route("/messages/<int:app_id>")
@login_required
def application_messages(app_id):
    application = get_application(app_id)
    if not application:
        return "Application not found", 404
    return render_template("message.html", application=application, applications=applications)












def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"pdf","doc","docx"}

def save_file(file_field, folder="UPLOAD_FOLDER"):
    if not file_field or file_field.filename == "":
        return None
    if not allowed_file(file_field.filename):
        return None

    filename = secure_filename(file_field.filename)
    upload_folder = app.config[folder]
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)
    file_field.save(file_path)

    # Store just the filename in DB
    return filename

app.config["RESUME_FOLDER"] = os.path.join(app.root_path, "files", "resumes")
app.config["DOCS_FOLDER"]   = os.path.join(app.root_path, "files", "documents")

os.makedirs(app.config["RESUME_FOLDER"], exist_ok=True)
os.makedirs(app.config["DOCS_FOLDER"], exist_ok=True)

class LoginUser(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.role = user.role
        self.name = user.name
        self.email = user.email

#app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecretkey123"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobportal.db'














# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = "login"   # redirect to login if not authenticated
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return LoginUser(user) if user else None

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Create tables immediately (Flask 3.0+)



@app.route("/")
def index():
    q = request.args.get("q", "")
    job_type = request.args.get("job_type", "")
    location = request.args.get("location", "")
    salary_min = request.args.get("salary_min", type=int)
    salary_max = request.args.get("salary_max", type=int)

    jobs = Job.query
    if q:
        jobs = jobs.filter(Job.title.ilike(f"%{q}%") | Job.description.ilike(f"%{q}%"))
    if job_type:
        jobs = jobs.filter_by(job_type=job_type)
    if location:
        jobs = jobs.filter(Job.location.ilike(f"%{location}%"))
    if salary_min is not None:
        jobs = jobs.filter(Job.salary_min >= salary_min)
    if salary_max is not None:
        jobs = jobs.filter(Job.salary_max <= salary_max)

    jobs = jobs.order_by(Job.created_at.desc()).all()
    return render_template("index.html", jobs=jobs, q=q, job_type=job_type, location=location, salary_min=salary_min, salary_max=salary_max)

@app.route("/search")
@login_required
def search():
    q = request.args.get("q")
    job_type = request.args.get("job_type")
    location = request.args.get("location")
    salary_min = request.args.get("salary_min")
    salary_max = request.args.get("salary_max")

    query = Job.query

    if q:
        query = query.filter(Job.title.ilike(f"%{q}%") | Job.description.ilike(f"%{q}%"))
    if job_type:
        query = query.filter_by(job_type=job_type)
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if salary_min:
        query = query.filter(Job.salary_min >= int(salary_min))
    if salary_max:
        query = query.filter(Job.salary_max <= int(salary_max))

    results = query.order_by(Job.created_at.desc()).all()

    return render_template("dashboard_seeker.html",
                           featured_jobs=results,
                           applications=Application.query.filter_by(seeker_id=current_user.id).all(),
                           q=q, job_type=job_type, location=location,
                           salary_min=salary_min, salary_max=salary_max)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Check if email already exists
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash("⚠️ Email already registered. Please log in.", "danger")
                return redirect(url_for("login"))

            # Hash password
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

            # Create new user
            new_user = User(
                role=form.role.data,
                name=form.name.data,
                email=form.email.data,
                password_hash=hashed_pw,
                company=form.company.data if form.role.data == "employer" else None,
                skills=form.skills.data if form.role.data == "seeker" else None,
                industry=form.industry.data if form.role.data == "employer" else None,
                resume_path=None
            )
            db.session.add(new_user)
            db.session.commit()

            flash("✅ Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            # Database error
            flash(f"❌ Database error: {str(e)}", "danger")
            return redirect(url_for("register"))

    else:
        if form.errors:
            # Show validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"⚠️ Error in {field}: {error}", "danger")

    return render_template("register.html", form=form)

   
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)



@app.route("/employer_applications/update/<int:app_id>", methods=["POST"])
def employer_applications_update(app_id):
    app_obj = Application.query.get_or_404(app_id)
    app_obj.status = request.form["status"]
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate reset token
            s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
            token = s.dumps(user.email, salt="password-reset-salt")
            
            print("Generated token:", token)
            # Build reset link
            reset_url = url_for("reset_password", token=token, _external=True)

            # Send email
            msg = Message("Password Reset Request",
                          recipients=[user.email])
            msg.body = f"Click the link to reset your password: {reset_url}"
            mail.send(msg)

            flash("Password reset link has been sent to your email.", "info")
            return redirect(url_for("login"))
        else:
            flash("No account found with that email.", "danger")

    return render_template("forgot_password.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        email = s.loads(token, salt="password-reset-salt", max_age=3600)  # 1 hour expiry
    except Exception:
        flash("The reset link is invalid or expired.", "danger")
        return redirect(url_for("forgot_password"))

    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)  # assuming you have set_password method
        db.session.commit()
        flash("Your password has been reset successfully.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", form=form, token=token)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "employer":
        jobs = Job.query.filter_by(employer_id=current_user.id).order_by(Job.created_at.desc()).all()
        return render_template("dashboard_employer.html", jobs=jobs)
    else:
        apps = Application.query.filter_by(seeker_id=current_user.id).order_by(Application.created_at.desc()).all()
        interviews = [a for a in apps if a.status == "interview"]

        featured_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()
        recommended_jobs = Job.query.limit(4).all()

        # Mock metrics
        unread_messages = 93
        profile_views = 45673

        # Chart data
        chart_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
        chart_applications = [12, 18, 22, 37]
        chart_interviews = [5, 9, 14, 22]
        chart_rejected = [2, 4, 6, 8]
        

        jobs = Job.query.all() 
        random.shuffle(jobs) 
        recommended_jobs = jobs[:4]

        return render_template(
            "dashboard_seeker.html",
            applications=apps,
            featured_jobs=featured_jobs,
            interviews=interviews,
            unread_messages=unread_messages,
            profile_views=profile_views,
            recommended_jobs=recommended_jobs,
            chart_labels=chart_labels,
            chart_applications=chart_applications,
            chart_interviews=chart_interviews,
            chart_rejected=chart_rejected
        )

@app.route("/recommended_jobs")
def recommended_jobs_partial():
    # Fetch all jobs
    jobs = Job.query.all()

    # Shuffle them randomly
    random.shuffle(jobs)

    # Take the first 6 after shuffle
    jobs = jobs[:6]

    # Render partial template
    return render_template("recommended_jobs_partial.html", jobs=jobs)


@app.route("/jobs/new", methods=["GET", "POST"])
@login_required
def job_new():
    if current_user.role != "employer":
        flash("Only employers can create jobs.", "warning")
        return redirect(url_for("index"))
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            description=form.description.data,
            qualifications=form.qualifications.data,
            responsibilities=form.responsibilities.data,
            location=form.location.data,
            job_type=form.job_type.data,
            salary_min=form.salary_min.data,
            salary_max=form.salary_max.data,
            employer_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        flash("Job created successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("job_form.html", form=form, action="Create")


@app.route("/jobs")
@login_required
def job_index():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template("job_index.html", jobs=jobs)

@app.route("/jobs/find", methods=["GET", "POST"])
@login_required
def find_jobs():
    if current_user.role != "seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    query = Job.query

    if request.method == "POST":
        keyword = request.form.get("keyword")
        location = request.form.get("location")
        job_type = request.form.get("job_type")
        mode = request.form.get("mode")
        salary_min = request.form.get("salary_min")
        salary_max = request.form.get("salary_max")

        if keyword:
            query = query.filter(Job.title.ilike(f"%{keyword}%") | Job.summary.ilike(f"%{keyword}%"))
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if job_type:
            query = query.filter_by(job_type=job_type)
        if salary_min:
            query = query.filter(Job.salary_min >= salary_min)
        if salary_max:
            query = query.filter(Job.salary_max <= salary_max)

    jobs = query.order_by(Job.created_at.desc()).all()

    
    return render_template("find_jobs.html", jobs=jobs)



@app.route("/jobs/applied")
@login_required
def applied_jobs():
    if current_user.role != "seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    apps = Application.query.filter_by(seeker_id=current_user.id).order_by(Application.created_at.desc()).all()
    return render_template("applied_jobs.html", applications=apps)



@app.route("/messages")
@login_required
def messages():
    if current_user.role != "seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    # Dummy applications with messages
    applications = [
        {
            "id": 1,
            "job_title": "Frontend Developer",
            "status": "applied",
            "messages": [
                {"sender": "Recruiter", "content": "We have received your application.", "timestamp": "2026-01-30"},
                {"sender": "HR Team", "content": "Your interview is scheduled for Feb 5th at 10 AM.", "timestamp": "2026-02-01"}
            ]
        },
        {
            "id": 2,
            "job_title": "Backend Developer",
            "status": "under review",
            "messages": [
                {"sender": "Recruiter", "content": "Your profile is being reviewed.", "timestamp": "2026-02-02"}
            ]
        }
    ]

    # Default: show first application’s messages
    selected_app = applications[0]

    return render_template("message.html", applications=applications, application=selected_app)



@app.route("/statistics")
@login_required
def statistics():
    apps = Application.query.filter_by(seeker_id=current_user.id).all()
    interviews = [a for a in apps if a.status == "interview"]
    rejected = [a for a in apps if a.status == "rejected"]

    stats = {
        "applications": len(apps),
        "interviews": len(interviews),
        "rejected": len(rejected)
    }

    chart_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
    chart_applications = [12, 18, 22, 37]
    chart_interviews = [5, 9, 14, 22]
    chart_rejected = [2, 4, 6, 8]

    return render_template(
        "statistics.html",
        stats=stats,
        chart_labels=chart_labels,
        chart_applications=chart_applications,
        chart_interviews=chart_interviews,
        chart_rejected=chart_rejected,
        now=datetime.now()   # 👈 pass now explicitly
    )




@app.route("/news")
@login_required
def news():
    if current_user.role != "seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    # Proper news items with IDs
    news_items = [
    {
        "id": 1,
        "title": "AI is transforming jobs",
        "source": "TechCrunch",
        "summary": "Artificial Intelligence is reshaping the job market with automation and new opportunities.",
        "details": "Full article text goes here. You can expand with more paragraphs, analysis, and insights.",
        "description": "This article explores how AI is impacting employment across industries.",
        "location": "Global",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Technology",
        "published_at": "2026-01-28"
    },
    {
        "id": 2,
        "title": "New hiring trends in 2026",
        "source": "BBC",
        "summary": "Employers are focusing on remote flexibility and skills-based hiring.",
        "details": "Detailed article content about hiring trends, statistics, and expert opinions.",
        "description": "An in-depth look at how hiring practices are evolving.",
        "location": "India",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Business",
        "published_at": "2026-01-29"
    },
    {
        "id": 3,
        "title": "Design careers on the rise",
        "source": "Forbes",
        "summary": "UI/UX and product design roles are in high demand across industries.",
        "details": "Full article text about design careers, salaries, and future outlook.",
        "description": "Exploring the growing demand for design professionals.",
        "location": "United States",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Design",
        "published_at": "2026-01-30"
    },
    {
        "id": 4,
        "title": "Remote work reshaping global offices",
        "source": "CNN Business",
        "summary": "Companies are rethinking office spaces as remote work becomes permanent.",
        "details": "Full article text about remote work, hybrid models, and office downsizing.",
        "description": "Examining the long-term impact of remote work on office culture.",
        "location": "Global",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Workplace",
        "published_at": "2026-01-31"
    },
    {
        "id": 5,
        "title": "Green jobs booming in renewable energy",
        "source": "The Guardian",
        "summary": "Renewable energy is driving demand for new green jobs worldwide.",
        "details": "Full article text about solar, wind, and sustainability careers.",
        "description": "Highlighting the rise of eco-friendly employment opportunities.",
        "location": "Europe",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Environment",
        "published_at": "2026-02-01"
    }
]


    return render_template("news.html", news_items=news_items)

@app.route("/news/<int:news_id>")
@login_required
def news_detail(news_id):
    news_items = [
    {
        "id": 1,
        "title": "AI is transforming jobs",
        "source": "TechCrunch",
        "summary": "Artificial Intelligence is reshaping the job market with automation and new opportunities.",
        "details": "Full article text goes here. You can expand with more paragraphs, analysis, and insights.",
        "description": "This article explores how AI is impacting employment across industries.",
        "location": "Global",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Technology",
        "published_at": "2026-01-28"
    },
    {
        "id": 2,
        "title": "New hiring trends in 2026",
        "source": "BBC",
        "summary": "Employers are focusing on remote flexibility and skills-based hiring.",
        "details": "Detailed article content about hiring trends, statistics, and expert opinions.",
        "description": "An in-depth look at how hiring practices are evolving.",
        "location": "India",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Business",
        "published_at": "2026-01-29"
    },
    {
        "id": 3,
        "title": "Design careers on the rise",
        "source": "Forbes",
        "summary": "UI/UX and product design roles are in high demand across industries.",
        "details": "Full article text about design careers, salaries, and future outlook.",
        "description": "Exploring the growing demand for design professionals.",
        "location": "United States",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Design",
        "published_at": "2026-01-30"
    },
    {
        "id": 4,
        "title": "Remote work reshaping global offices",
        "source": "CNN Business",
        "summary": "Companies are rethinking office spaces as remote work becomes permanent.",
        "details": "Full article text about remote work, hybrid models, and office downsizing.",
        "description": "Examining the long-term impact of remote work on office culture.",
        "location": "Global",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Workplace",
        "published_at": "2026-01-31"
    },
    {
        "id": 5,
        "title": "Green jobs booming in renewable energy",
        "source": "The Guardian",
        "summary": "Renewable energy is driving demand for new green jobs worldwide.",
        "details": "Full article text about solar, wind, and sustainability careers.",
        "description": "Highlighting the rise of eco-friendly employment opportunities.",
        "location": "Europe",
        "image_url": "https://via.placeholder.com/600x300",
        "category": "Environment",
        "published_at": "2026-02-01"
    }
]


    news_item = next((n for n in news_items if n["id"] == news_id), None)
    if not news_item:
        abort(404)
    return render_template("news_detail.html", news_item=news_item)


jobs = [
    {
        "id": 1,
        "title": "Frontend Developer",
        "company": "TechCorp Pvt Ltd",
        "location": "Pune, India",
        "summary": "Work on modern web applications with React and Vue.",
        "details": "As a Frontend Developer, you will design and build user interfaces, collaborate with backend teams, and ensure responsive design.",
        "criteria": [
            "Bachelor’s degree in Computer Science or related field",
            "2+ years of experience in frontend development",
            "Proficiency in HTML, CSS, JavaScript, React/Vue",
            "Strong understanding of UI/UX principles"
        ],
        "published_at": "2026-01-28"
    },
    {
        "id": 2,
        "title": "Data Analyst",
        "company": "Insight Analytics",
        "location": "Mumbai, India",
        "summary": "Analyze datasets to provide business insights.",
        "details": "You will work with large datasets, create dashboards, and support decision-making with data-driven insights.",
        "criteria": [
            "Bachelor’s degree in Statistics, Mathematics, or related field",
            "Experience with SQL and Python",
            "Knowledge of data visualization tools (Tableau/Power BI)",
            "Strong analytical and problem-solving skills"
        ],
        "published_at": "2026-01-29"
    }
]



@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def job_edit(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user.role != "employer" or job.employer_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("index"))
    form = JobForm(obj=job)
    if form.validate_on_submit():
        form.populate_obj(job)
        db.session.commit()
        flash("Job updated.", "success")
        return redirect(url_for("dashboard"))
    return render_template("job_form.html", form=form, action="Edit")

@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
def job_delete(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user.role != "employer" or job.employer_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("index"))
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted.", "info")
    return redirect(url_for("dashboard"))

@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template("job_detail.html", job=job)

@app.route("/jobs/<int:job_id>")
@login_required
def job_detail1(job_id):
    job = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        abort(404)
    return render_template("job_detail1.html", job=job)


@app.route("/jobs")
@login_required
def jobs_index():
    if current_user.role != "seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("jobs_index.html", jobs=jobs)

@app.route("/jobs/<int:job_id>/apply", methods=["GET", "POST"])
@login_required
def job_apply(job_id):
    if current_user.role != "seeker":
        flash("Only job seekers can apply.", "warning")
        return redirect(url_for("index"))
    job = Job.query.get_or_404(job_id)
    form = ApplicationForm()
    if form.validate_on_submit():
        resume_url = None
        user = User.query.get(current_user.id)
        if user.resume_path:
            resume_url = f"/uploads/{os.path.basename(user.resume_path)}"
        app_obj = Application(
            job_id=job.id,
            seeker_id=current_user.id,
            cover_letter=form.cover_letter.data,
            resume_url=resume_url
        )
        db.session.add(app_obj)
        db.session.commit()
        flash("Application submitted.", "success")
        return redirect(url_for("dashboard"))
    return render_template("applications.html", form=form, job=job)



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get_or_404(current_user.id)
    form = ProfileForm(obj=user)

    if request.method == "POST":
        print("➡️ Received POST request")
        print("Form data:", request.form)
        print("Files:", request.files)

    if form.validate_on_submit():
        print("✅ Form validated successfully")

        # Personal
        user.name = form.name.data
        user.phone = form.phone.data
        user.birthday = form.birthday.data
        user.nationality = form.nationality.data

        # Education
        user.degree = form.degree.data
        user.institution = form.institution.data
        user.graduation_year = form.graduation_year.data
        user.major = form.major.data

        # Professional
        user.current_position = form.current_position.data
        user.company = form.company.data
        user.experience_years = form.experience_years.data
        user.skills = form.skills.data

        # Employer-only
        if current_user.role == "employer":
            user.company_name = form.company_name.data
            user.company_contact = form.company_contact.data
            user.employee_id = form.employee_id.data
            user.department = form.department.data
            user.designation = form.designation.data
            user.reporting_to = form.reporting_to.data
            user.joined_on = form.joined_on.data
            user.status = form.status.data
            user.notice_period = form.notice_period.data

        # Documents
        if form.other_docs.data:
            user.other_docs_path = save_file(form.other_docs.data, folder="DOCS_FOLDER")

        # Resume (seeker only)
        if current_user.role == "seeker" and form.resume.data:
            user.resume_path = save_file(form.resume.data, folder="RESUME_FOLDER")

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    if form.errors:
        print("❌ Form errors:", form.errors)

    return render_template("profile.html", form=form, user=user)


@app.route("/resumes/<filename>")
@login_required
def get_resume(filename):
    return send_from_directory(app.config["RESUME_FOLDER"], filename)

@app.route("/documents/<filename>")
@login_required
def get_document(filename):
    return send_from_directory(app.config["DOCS_FOLDER"], filename)


@app.route("/uploads/<path:filename>")
@login_required
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/employer/applications")
@login_required
def employer_applications():
    if current_user.role != "employer":
        flash("Only employers can view applications.", "warning")
        return redirect(url_for("index"))

    # Get all jobs posted by this employer
    jobs = Job.query.filter_by(employer_id=current_user.id).all()
    job_ids = [job.id for job in jobs]

    # Get all applications for those jobs
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all()

    return render_template("employer_applications.html", applications=applications)

@app.route('/employer/jobs')
@login_required
def employer_jobs():
    # Query all jobs posted by the current employer
    jobs = Job.query.filter_by(employer_id=current_user.id).all()
    
    return render_template(
        "employer_jobs.html",   # create this template
        jobs=jobs
    )

@app.route("/applications/<int:app_id>/delete", methods=["POST"])
@login_required
def delete_application(app_id):
    app_obj = Application.query.get_or_404(app_id)

    # Only allow employer who owns the job to delete
    if current_user.role != "employer" or app_obj.job.employer_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(app_obj)
    db.session.commit()
    flash("Application deleted.", "info")
    return redirect(url_for("dashboard"))



if __name__ == "__main__":
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()


        # ✅ Quick schema check for jobs table
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns("jobs")
        print("Jobs table columns:")
        for col in columns:
            print(f"- {col['name']} ({col['type']})")

    app.run(debug=True)