from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user # type: ignore
from functools import wraps
from models.models import db
from models.models import Trainer, Member, WorkoutSchedule, Attendance
from datetime import date

trainer_bp = Blueprint('trainer', __name__)

def trainer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('admin', 'trainer'):
            flash('Trainer access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@trainer_bp.route('/dashboard')
@login_required
@trainer_required
def dashboard():
    trainer = current_user.trainer
    members = Member.query.filter_by(id=trainer.id).all() if trainer else []
    schedules = WorkoutSchedule.query.filter_by(id=trainer.id).all() if trainer else []
    today_att = Attendance.query.filter_by(date=date.today()).count()
    return render_template('trainer/dashboard.html', trainer=trainer,
                           members=members, schedules=schedules, today_att=today_att)

@trainer_bp.route('/members')
@login_required
@trainer_required
def members():
    trainer = current_user.trainer
    members = Member.query.filter_by(id=trainer.id).all() if trainer else []
    return render_template('trainer/members.html', members=members, trainer=trainer)

@trainer_bp.route('/schedules')
@login_required
@trainer_required
def schedules():
    trainer = current_user.trainer
    schedules = WorkoutSchedule.query.filter_by(id=trainer.id).all() if trainer else []
    return render_template('trainer/schedules.html', schedules=schedules, trainer=trainer)

@trainer_bp.route('/schedules/add', methods=['GET', 'POST'])
@login_required
@trainer_required
def add_schedule():
    trainer = current_user.trainer
    if request.method == 'POST' and trainer:
        schedule = WorkoutSchedule(
            id=trainer.id,
            workout_type=request.form.get('workout_type'),
            time_slot=request.form.get('time_slot'),
            day_of_week=request.form.get('day_of_week'),
            capacity=request.form.get('capacity', type=int, default=20)
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Schedule added!', 'success')
        return redirect(url_for('trainer.schedules'))
    return render_template('trainer/schedule_form.html', trainer=trainer, schedule=None)

@trainer_bp.route('/schedules/delete/<int:id>', methods=['POST'])
@login_required
@trainer_required
def delete_schedule(id):
    schedule = WorkoutSchedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted.', 'success')
    return redirect(url_for('trainer.schedules'))
