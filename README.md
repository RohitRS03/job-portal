# Job Portal System 💼

## 📌 Introduction
The Job Portal System is a web-based application designed to connect job seekers with employers. It provides a platform where candidates can register, upload resumes, search for jobs, and apply online, while employers can post vacancies, manage applications, and shortlist candidates.

---

## 🚀 Features
- **User Registration & Login**
  - Job seekers and employers can create accounts
- **Profile Management**
  - Resume upload, skills, and experience tracking
- **Job Posting & Management**
  - Employers can add, edit, and delete job postings
- **Job Search & Apply**
  - Advanced filters by location, skills, and salary
- **Admin Dashboard**
  - Manage users, jobs, and reports
- **Notifications**
  - Application status updates
- **Secure Authentication**
  - Password hashing, session management, role-based access

---

## 🛠️ Technology Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask/Django)
- **Database:** MySQL/PostgreSQL
- **Security:** Password hashing, CSRF protection

---

## 📂 Project Structure

job-portal/
│── Backend/
│   ├── app.py
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   └── static/
│── README.md
│── requirements.txt


---

## ⚙️ Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/job-portal.git
   cd job-portal/Backend
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

pip install -r requirements.txt

flask run
Open in browser: http://127.0.0.1:5000
