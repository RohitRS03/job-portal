from app import app, db
from models import User, Job
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    employer_pw = bcrypt.generate_password_hash("employer123").decode("utf-8")
    seeker_pw = bcrypt.generate_password_hash("seeker123").decode("utf-8")

    employer = User(role="employer", name="Acme HR", email="employer@example.com",
                    password_hash=employer_pw, company="Acme Corp")
    seeker = User(role="seeker", name="Alice Kumar", email="seeker@example.com",
                  password_hash=seeker_pw)

    db.session.add_all([employer, seeker])
    db.session.commit()

    job1 = Job(
        title="Senior Backend Engineer",
        description="Design scalable APIs and microservices.",
        qualifications="Python, Flask, SQL, Docker",
        responsibilities="Build, test, deploy services",
        location="Pune, MH",
        job_type="Full-time",
        salary_min=800000,
        salary_max=1600000,
        employer_id=employer.id
    )
    job2 = Job(
        title="Frontend Developer (React)",
        description="Create responsive UI with React.",
        qualifications="React, JS, CSS, REST",
        responsibilities="Build and optimize UI",
        location="Remote",
        job_type="Remote",
        salary_min=600000,
        salary_max=1200000,
        employer_id=employer.id
    )
    db.session.add_all([job1, job2])
    db.session.commit()

    print("Database seeded with sample users and jobs.")
