from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response
from flask_login import login_required, current_user
from functools import wraps
from models.models import db,Member, Trainer, MembershipPlan, Payment, Attendance, WorkoutSchedule, User
from werkzeug.security import generate_password_hash
from datetime import date, datetime, timedelta
import csv, io

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_members = Member.query.count()
    total_trainers = Trainer.query.count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='Paid').scalar() or 0
    today_attendance = Attendance.query.filter_by(date=date.today()).count()
    expiring_soon = [m for m in Member.query.all() if m.days_to_expiry is not None and 0 <= m.days_to_expiry <= 7]
    expired = [m for m in Member.query.all() if m.is_expired]

    # Monthly revenue for chart (last 6 months)
    monthly_revenue = []
    monthly_labels = []
    for i in range(5, -1, -1):
        d = date.today().replace(day=1) - timedelta(days=i*30)
        label = d.strftime('%b %Y')
        rev = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.status == 'Paid',
            db.extract('month', Payment.payment_date) == d.month,
            db.extract('year', Payment.payment_date) == d.year
        ).scalar() or 0
        monthly_labels.append(label)
        monthly_revenue.append(float(rev))

    # Attendance last 7 days
    att_labels = []
    att_data = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        count = Attendance.query.filter_by(date=d).count()
        att_labels.append(d.strftime('%a'))
        att_data.append(count)

    # Plan distribution
    plan_labels = [p.plan_name for p in MembershipPlan.query.all()]
    plan_data = [Member.query.filter_by(plan_id=p.id).count() for p in MembershipPlan.query.all()]

    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
    recent_members = Member.query.order_by(Member.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_members=total_members, total_trainers=total_trainers,
        total_revenue=total_revenue, today_attendance=today_attendance,
        expiring_soon=expiring_soon, expired=expired,
        monthly_labels=monthly_labels, monthly_revenue=monthly_revenue,
        att_labels=att_labels, att_data=att_data,
        plan_labels=plan_labels, plan_data=plan_data,
        recent_payments=recent_payments, recent_members=recent_members)

# ─── MEMBERS ────────────────────────────────────────────────────────────────

@admin_bp.route('/members')
@login_required
@admin_required
def members():
    q = request.args.get('q', '')
    gender = request.args.get('gender', '')
    plan_id = request.args.get('plan_id', '')
    query = Member.query
    if q:
        query = query.filter(Member.name.ilike(f'%{q}%') | Member.email.ilike(f'%{q}%') | Member.contact.ilike(f'%{q}%'))
    if gender:
        query = query.filter_by(gender=gender)
    if plan_id:
        query = query.filter_by(plan_id=int(plan_id))
    members = query.order_by(Member.created_at.desc()).all()
    plans = MembershipPlan.query.all()
    return render_template('admin/members.html', members=members, plans=plans, q=q)

@admin_bp.route('/members/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_member():
    plans = MembershipPlan.query.all()
    trainers = Trainer.query.all()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('admin/member_form.html', plans=plans, trainers=trainers)

        user = User(username=username, email=email, role='member')
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.flush()

        # Handle trainer_id safely
        trainer_id_raw = request.form.get('trainer_id', '').strip()
        trainer_id = int(trainer_id_raw) if trainer_id_raw else None

        # Handle plan_id safely
        plan_id_raw = request.form.get('plan_id', '').strip()
        plan_id = int(plan_id_raw) if plan_id_raw else None

        member = Member(
            name=request.form['name'],
            age=request.form.get('age', type=int),
            gender=request.form.get('gender'),
            contact=request.form.get('contact'),
            email=email,
            join_date=date.fromisoformat(request.form.get('join_date', str(date.today()))),
            health_details=request.form.get('health_details'),
            plan_id=plan_id,
            trainer_id=trainer_id,
            user_id=user.id
        )
        db.session.add(member)
        db.session.commit()
        flash('Member added successfully!', 'success')
        return redirect(url_for('admin.members'))
    return render_template('admin/member_form.html', plans=plans, trainers=trainers, member=None)

@admin_bp.route('/members/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_member(id):
    member = Member.query.get_or_404(id)
    plans = MembershipPlan.query.all()
    trainers = Trainer.query.all()
    if request.method == 'POST':
        member.name = request.form['name']
        member.age = request.form.get('age', type=int)
        member.gender = request.form.get('gender')
        member.contact = request.form.get('contact')
        member.email = request.form.get('email')
        member.health_details = request.form.get('health_details')
        member.plan_id = request.form.get('plan_id', type=int)
        member.id = request.form.get('id', type=int) or None
        db.session.commit()
        flash('Member updated!', 'success')
        return redirect(url_for('admin.members'))
    return render_template('admin/member_form.html', member=member, plans=plans, trainers=trainers)

@admin_bp.route('/members/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_member(id):
    member = Member.query.get_or_404(id)
    if member.user:
        db.session.delete(member.user)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted.', 'success')
    return redirect(url_for('admin.members'))

@admin_bp.route('/members/view/<int:id>')
@login_required
@admin_required
def view_member(id):
    member = Member.query.get_or_404(id)
    return render_template('admin/member_detail.html', member=member)

# ─── TRAINERS ────────────────────────────────────────────────────────────────

@admin_bp.route('/trainers')
@login_required
@admin_required
def trainers():
    q = request.args.get('q', '')
    spec = request.args.get('spec', '')
    query = Trainer.query
    if q:
        query = query.filter(Trainer.name.ilike(f'%{q}%'))
    if spec:
        query = query.filter(Trainer.specialization.ilike(f'%{spec}%'))
    trainers = query.all()
    return render_template('admin/trainers.html', trainers=trainers, q=q)

@admin_bp.route('/trainers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_trainer():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('admin/trainer_form.html', trainer=None)
        user = User(username=username, email=email,
                    password=generate_password_hash(request.form['password']), role='trainer')
        db.session.add(user)
        db.session.flush()
        trainer = Trainer(name=request.form['name'],
                          specialization=request.form.get('specialization'),
                          contact_phone=request.form.get('contact_phone'),
                          contact_email=request.form.get('contact_email'),
                          experience=request.form.get('experience', type=int, default=0),
                          user_id=user.id)
        db.session.add(trainer)
        db.session.commit()
        flash('Trainer added!', 'success')
        return redirect(url_for('admin.trainers'))
    return render_template('admin/trainer_form.html', trainer=None)

@admin_bp.route('/trainers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trainer(id):
    trainer = Trainer.query.get_or_404(id)
    if request.method == 'POST':
        trainer.name = request.form['name']
        trainer.specialization = request.form.get('specialization')
        trainer.contact_phone = request.form.get('contact_phone')
        trainer.contact_email=request.form.get('contact_email'),
        trainer.experience = request.form.get('experience', type=int, default=0)
        db.session.commit()
        flash('Trainer updated!', 'success')
        return redirect(url_for('admin.trainers'))
    return render_template('admin/trainer_form.html', trainer=trainer)

@admin_bp.route('/trainers/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_trainer(id):
    trainer = Trainer.query.get_or_404(id)
    if trainer.user:
        db.session.delete(trainer.user)
    db.session.delete(trainer)
    db.session.commit()
    flash('Trainer deleted.', 'success')
    return redirect(url_for('admin.trainers'))

# ─── PLANS ───────────────────────────────────────────────────────────────────

@admin_bp.route('/plans')
@login_required
@admin_required
def plans():
    plans = MembershipPlan.query.all()
    return render_template('admin/plans.html', plans=plans)

@admin_bp.route('/plans/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_plan():
    if request.method == 'POST':
        plan = MembershipPlan(plan_name=request.form['plan_name'],
                              duration=request.form.get('duration', type=int),
                              fees=request.form.get('fees', type=float),
                              benefits=request.form.get('benefits'))
        db.session.add(plan)
        db.session.commit()
        flash('Plan created!', 'success')
        return redirect(url_for('admin.plans'))
    return render_template('admin/plan_form.html', plan=None)

@admin_bp.route('/plans/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_plan(id):
    plan = MembershipPlan.query.get_or_404(id)
    if request.method == 'POST':
        plan.plan_name = request.form['plan_name']
        plan.duration = request.form.get('duration', type=int)
        plan.fees = request.form.get('fees', type=float)
        plan.benefits = request.form.get('benefits')
        db.session.commit()
        flash('Plan updated!', 'success')
        return redirect(url_for('admin.plans'))
    return render_template('admin/plan_form.html', plan=plan)

@admin_bp.route('/plans/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_plan(id):
    plan = MembershipPlan.query.get_or_404(id)
    db.session.delete(plan)
    db.session.commit()
    flash('Plan deleted.', 'success')
    return redirect(url_for('admin.plans'))

# ─── PAYMENTS ────────────────────────────────────────────────────────────────

@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    status = request.args.get('status', '')
    query = Payment.query
    if status:
        query = query.filter_by(status=status)
    payments = query.order_by(Payment.payment_date.desc()).all()
    members = Member.query.all()
    return render_template('admin/payments.html', payments=payments, members=members)

@admin_bp.route('/payments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_payment():
    members = Member.query.all()
    if request.method == 'POST':
        payment = Payment(
            member_id=request.form.get('member_id', type=int),
            amount=request.form.get('amount', type=float),
            payment_date=date.fromisoformat(request.form.get('payment_date', str(date.today()))),
            payment_mode=request.form.get('payment_mode'),
            status=request.form.get('status', 'Paid'),
            notes=request.form.get('notes')
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment recorded!', 'success')
        return redirect(url_for('admin.payments'))
    return render_template('admin/payment_form.html', members=members, payment=None, today=str(date.today()))

@admin_bp.route('/payments/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    flash('Payment deleted.', 'success')
    return redirect(url_for('admin.payments'))

# ─── ATTENDANCE ───────────────────────────────────────────────────────────────

@admin_bp.route('/attendance')
@login_required
@admin_required
def attendance():
    filter_date = request.args.get('date', str(date.today()))
    member_id = request.args.get('member_id', '')
    query = Attendance.query
    try:
        query = query.filter_by(date=date.fromisoformat(filter_date))
    except:
        pass
    if member_id:
        query = query.filter_by(member_id=int(member_id))
    records = query.order_by(Attendance.check_in).all()
    members = Member.query.all()
    return render_template('admin/attendance.html', records=records, members=members,
                           filter_date=filter_date)

@admin_bp.route('/attendance/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_attendance():
    members = Member.query.all()
    if request.method == 'POST':
        att = Attendance(
            member_id=request.form.get('member_id', type=int),
            date=date.fromisoformat(request.form.get('date', str(date.today()))),
            check_in=request.form.get('check_in'),
            check_out=request.form.get('check_out')
        )
        db.session.add(att)
        db.session.commit()
        flash('Attendance recorded!', 'success')
        return redirect(url_for('admin.attendance'))
    return render_template('admin/attendance_form.html', members=members, today=str(date.today()))
# ─── SCHEDULES ────────────────────────────────────────────────────────────────

@admin_bp.route('/schedules')
@login_required
@admin_required
def schedules():
    trainers = Trainer.query.all()
    schedules = WorkoutSchedule.query.order_by(WorkoutSchedule.day_of_week).all()
    return render_template('admin/schedules.html', schedules=schedules, trainers=trainers)

@admin_bp.route('/schedules/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_schedule():
    trainers = Trainer.query.all()
    if request.method == 'POST':
        trainer_id = request.form.get('trainer_id', type=int)
        if not trainer_id:
            flash('Please select a trainer!', 'danger')
            return render_template('admin/schedule_form.html', trainers=trainers, schedule=None)
        schedule = WorkoutSchedule(
            trainer_id=trainer_id,
            workout_type=request.form.get('workout_type'),
            time_slot=request.form.get('time_slot'),
            day_of_week=request.form.get('day_of_week'),
            capacity=request.form.get('capacity', type=int, default=20)
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Schedule added!', 'success')
        return redirect(url_for('admin.schedules'))
    return render_template('admin/schedule_form.html', trainers=trainers, schedule=None)

@admin_bp.route('/schedules/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_schedule(id):
    schedule = WorkoutSchedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted.', 'success')
    return redirect(url_for('admin.schedules'))

# ─── EXPORT CSV ──────────────────────────────────────────────────────────────

@admin_bp.route('/export/members')
@login_required
@admin_required
def export_members():
    members = Member.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Age', 'Gender', 'Contact', 'Email', 'Join Date', 'Plan', 'Expiry', 'Status'])
    for m in members:
        writer.writerow([m.id, m.name, m.age, m.gender, m.contact, m.email,
                         m.join_date, m.plan.plan_name if m.plan else '',
                         m.expiry_date, 'Expired' if m.is_expired else 'Active'])
    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=members.csv'})

@admin_bp.route('/export/payments')
@login_required
@admin_required
def export_payments():
    payments = Payment.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Member', 'Amount', 'Date', 'Mode', 'Status'])
    for p in payments:
        writer.writerow([p.id, p.member.name if p.member else '', p.amount,
                         p.payment_date, p.payment_mode, p.status])
    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=payments.csv'})
