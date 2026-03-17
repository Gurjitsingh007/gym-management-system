# 🏋️ FitCore Pro — Gym Management System

A full-stack web application built with **Flask + SQLAlchemy + SQLite**, featuring a modern dark/light UI.

---

## 🚀 Quick Setup (5 minutes)

### 1. Clone / Download the project
```bash
cd gym_management
```

### 2. Create & activate virtual environment
```bash
python3 -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

---

## 🔐 Demo Login Credentials

| Role    | Username  | Password   |
|---------|-----------|------------|
| Admin   | admin     | admin123   |
| Trainer | trainer1  | trainer123 |
| Member  | member1   | member123  |

---

## 📁 Project Structure

```
gym_management/
├── app.py                  ← Main Flask app + seed data
├── requirements.txt        ← Python dependencies
├── models/
│   ├── __init__.py
│   └── models.py           ← All SQLAlchemy models
├── routes/
│   ├── __init__.py
│   ├── auth.py             ← Login/Logout
│   ├── admin.py            ← Admin routes
│   ├── trainer.py          ← Trainer routes
│   └── member.py           ← Member routes
├── templates/
│   ├── base.html           ← Base layout with sidebar
│   ├── auth/
│   │   └── login.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── members.html / member_form.html / member_detail.html
│   │   ├── trainers.html / trainer_form.html
│   │   ├── plans.html / plan_form.html
│   │   ├── payments.html / payment_form.html
│   │   ├── attendance.html / attendance_form.html
│   │   └── schedules.html / schedule_form.html
│   ├── trainer/
│   │   ├── dashboard.html / members.html
│   │   └── schedules.html / schedule_form.html
│   └── member/
│       ├── dashboard.html / profile.html
│       ├── payments.html
│       └── attendance.html
└── static/
    ├── css/style.css       ← Full custom CSS (dark/light themes)
    └── js/main.js          ← Theme toggle, animations, sidebar
```

---

## 🗃️ Database Schema

```sql
users           → id, username, email, password, role
members         → id, name, age, gender, contact, email, join_date, health_details, plan_id, id, user_id
trainers        → id, name, specialization, phone, experience, user_id
membership_plans → id, plan_name, duration, fees, benefits
payments        → id, member_id, amount, payment_date, payment_mode, status, notes
attendance      → id, member_id, date, check_in, check_out
workout_schedules → id, id, workout_type, time_slot, day_of_week, capacity
```

---

## ✨ Features

| Module             | Features |
|--------------------|----------|
| 🏠 Dashboard        | Live stats, Chart.js charts, recent activity, alerts |
| 👥 Members          | Full CRUD, search/filter, CSV export, expiry alerts |
| 🏋️ Trainers        | CRUD, card view, assigned members |
| 📋 Plans            | CRUD, benefit listings, enrollment counts |
| 💳 Payments         | Record/delete, filter by status, CSV export |
| 📅 Attendance       | Daily tracking, check-in/out, history view |
| 📆 Schedules        | Weekly calendar view, trainer assignment |
| 🔐 Auth             | Role-based login (admin/trainer/member) |
| 🌙 Theme            | Dark/Light mode toggle, persists via localStorage |
| 📱 Responsive       | Mobile-friendly sidebar, responsive tables |

---

## 💡 Tech Stack

- **Backend**: Python 3 + Flask 3.0
- **ORM**: SQLAlchemy + Flask-SQLAlchemy
- **Database**: SQLite (dev) — easily swap to MySQL/PostgreSQL
- **Auth**: Flask-Login with role-based access control
- **Frontend**: Custom CSS (no Bootstrap/Tailwind) + Vanilla JS
- **Charts**: Chart.js 4
- **Icons**: Font Awesome 6
- **Fonts**: Syne + DM Sans (Google Fonts)

---

## 🔄 Switch to MySQL

In `app.py`, change:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
# ↓ Replace with:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/gymdb'
```
Then: `pip install pymysql`

