from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models.models import Member, Payment, Attendance, WorkoutSchedule
from models.models import db

member_bp = Blueprint('member', __name__)

def member_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('admin', 'member'):
            flash('Member access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@member_bp.route('/dashboard')
@login_required
@member_required
def dashboard():
    member = current_user.member
    if not member:
        flash('Member profile not found.', 'danger')
        return redirect(url_for('auth.logout'))
    payments = Payment.query.filter_by(id=member.id).order_by(Payment.payment_date.desc()).limit(5).all()
    attendance = Attendance.query.filter_by(id=member.id).order_by(Attendance.date.desc()).limit(10).all()
    schedules = WorkoutSchedule.query.all()
    total_visits = Attendance.query.filter_by(id=member.id).count()
    return render_template('member/dashboard.html', member=member,
                           payments=payments, attendance=attendance,
                           schedules=schedules, total_visits=total_visits)

@member_bp.route('/profile')
@login_required
@member_required
def profile():
    member = current_user.member
    return render_template('member/profile.html', member=member)

@member_bp.route('/payments')
@login_required
@member_required
def payments():
    member = current_user.member
    payments = Payment.query.filter_by(id=member.id).order_by(Payment.payment_date.desc()).all()
    return render_template('member/payments.html', member=member, payments=payments)

@member_bp.route('/attendance')
@login_required
@member_required
def attendance():
    member = current_user.member
    records = Attendance.query.filter_by(id=member.id).order_by(Attendance.date.desc()).all()
    return render_template('member/attendance.html', member=member, records=records)
