from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    member = db.relationship('Member', backref='user', uselist=False)
    trainer = db.relationship('Trainer', backref='user', uselist=False)

    def set_password(self, password):        # ← ADD THIS
        self.password = generate_password_hash(password)

    def check_password(self, password):      # ← ADD THIS
        return check_password_hash(self.password, password)


class MembershipPlan(db.Model):
    __tablename__ = 'membership_plans'
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    fees = db.Column(db.Float, nullable=False)
    benefits = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('Member', backref='plan', lazy=True)


class Trainer(db.Model):
    __tablename__ = 'trainers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(150))
    contact_phone = db.Column(db.String(20))        # ← ADD
    contact_email = db.Column(db.String(120))       # ← ADD
    bio = db.Column(db.Text)                        # ← ADD
    experience = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    schedules = db.relationship('WorkoutSchedule', backref='trainer', lazy=True)
    members = db.relationship('Member', backref='trainer', lazy=True)


class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    contact = db.Column(db.String(15))
    email = db.Column(db.String(120))
    join_date = db.Column(db.Date, default=date.today)
    health_details = db.Column(db.Text)
    plan_id = db.Column(db.Integer, db.ForeignKey('membership_plans.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship('Payment', backref='member', lazy=True)
    attendance = db.relationship('Attendance', backref='member', lazy=True)

    @property
    def expiry_date(self):
        if self.plan and self.join_date:
            months = self.plan.duration
            new_month = self.join_date.month + months
            new_year = self.join_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            try:
                return self.join_date.replace(year=new_year, month=new_month)
            except:
                return None
        return None

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False

    @property
    def days_to_expiry(self):
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return None

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments if p.status == 'Paid')


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=date.today)
    payment_mode = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    check_in = db.Column(db.String(10))
    check_out = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WorkoutSchedule(db.Model):
    __tablename__ = 'workout_schedules'
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    workout_type = db.Column(db.String(100))
    time_slot = db.Column(db.String(50))
    day_of_week = db.Column(db.String(20))
    capacity = db.Column(db.Integer, default=20)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
