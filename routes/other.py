from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, Member, Trainer, WorkoutSchedule, Attendance, Payment
from datetime import date, datetime

trainer_bp = Blueprint('trainer', __name__, url_prefix='/trainer')
member_bp = Blueprint('member', __name__, url_prefix='/member')

def trainer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('admin', 'trainer'):
            flash('Trainer access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# ─── TRAINER ROUTES ───────────────────────────────────────────────────────────
@trainer_bp.route('/dashboard')
@login_required
@trainer_required
def dashboard():
    trainer = Trainer.query.filter_by(user_id=current_user.id).first()
    schedules = WorkoutSchedule.query.filter_by(is_active=True)
    if trainer:
        schedules = schedules.filter_by(id=trainer.id)
    schedules = schedules.all()
    members = Member.query.filter_by(is_active=True).all()
    today_att = Attendance.query.filter_by(date=date.today()).count()
    return render_template('trainer/dashboard.html', trainer=trainer,
                           schedules=schedules, members=members, today_att=today_att)

@trainer_bp.route('/members')
@login_required
@trainer_required
def members():
    members = Member.query.filter_by(is_active=True).all()
    return render_template('trainer/members.html', members=members)

@trainer_bp.route('/schedules')
@login_required
@trainer_required
def schedules():
    trainer = Trainer.query.filter_by(user_id=current_user.id).first()
    all_trainers = Trainer.query.filter_by(is_active=True).all()
    if trainer:
        schedules = WorkoutSchedule.query.filter_by(id=trainer.id, is_active=True).all()
    else:
        schedules = WorkoutSchedule.query.filter_by(is_active=True).all()
    return render_template('trainer/schedules.html', schedules=schedules, trainer=trainer, all_trainers=all_trainers)

@trainer_bp.route('/schedules/add', methods=['POST'])
@login_required
@trainer_required
def add_schedule():
    trainer = Trainer.query.filter_by(user_id=current_user.id).first()
    id = trainer.id if trainer else int(request.form.get('id', 1))
    schedule = WorkoutSchedule(
        id=id,
        workout_types=request.form.get('workout_types'),
        time_slot=request.form.get('time_slot'),
        day_of_week=request.form.get('day_of_week'),
        description=request.form.get('description'),
        max_capacity=int(request.form.get('max_capacity', 20))
    )
    db.session.add(schedule)
    db.session.commit()
    flash('Schedule added!', 'success')
    return redirect(url_for('trainer.schedules'))

# ─── MEMBER ROUTES ────────────────────────────────────────────────────────────
@member_bp.route('/dashboard')
@login_required
@member_required
def dashboard():
    member = Member.query.filter_by(user_id=current_user.id).first()
    if not member:
        flash('No member profile linked to your account.', 'warning')
        return render_template('member/dashboard.html', member=None)
    recent_payments = Payment.query.filter_by(id=member.id).order_by(Payment.payment_date.desc()).limit(3).all()
    recent_attendance = Attendance.query.filter_by(id=member.id).order_by(Attendance.date.desc()).limit(5).all()
    schedules = WorkoutSchedule.query.filter_by(is_active=True).all()
    return render_template('member/dashboard.html', member=member,
                           recent_payments=recent_payments,
                           recent_attendance=recent_attendance,
                           schedules=schedules)

@member_bp.route('/profile')
@login_required
@member_required
def profile():
    member = Member.query.filter_by(user_id=current_user.id).first()
    return render_template('member/profile.html', member=member)

@member_bp.route('/payments')
@login_required
@member_required
def payments():
    member = Member.query.filter_by(user_id=current_user.id).first()
    if not member:
        return render_template('member/payments.html', payments=[], member=None)
    payments = Payment.query.filter_by(id=member.id).order_by(Payment.payment_date.desc()).all()
    return render_template('member/payments.html', payments=payments, member=member)

@member_bp.route('/attendance')
@login_required
@member_required
def attendance():
    member = Member.query.filter_by(user_id=current_user.id).first()
    if not member:
        return render_template('member/attendance.html', records=[], member=None)
    records = Attendance.query.filter_by(id=member.id).order_by(Attendance.date.desc()).all()
    total = len(records)
    this_month = sum(1 for r in records if r.date.month == date.today().month and r.date.year == date.today().year)
    return render_template('member/attendance.html', records=records, member=member,
                           total=total, this_month=this_month)

@member_bp.route('/schedules')
@login_required
@member_required
def schedules():
    schedules = WorkoutSchedule.query.filter_by(is_active=True).all()
    return render_template('member/schedules.html', schedules=schedules)
