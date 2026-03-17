from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from models.models import db, User, Member, Trainer, MembershipPlan, Payment, Attendance, WorkoutSchedule
from routes import auth_bp, admin_bp, trainer_bp, member_bp
from datetime import date, timedelta
import datetime as dt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(trainer_bp, url_prefix='/trainer')
    app.register_blueprint(member_bp, url_prefix='/member')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.template_filter('currency')
    def currency_filter(value):
        return 'Rs.{:,.0f}'.format(value)

    @app.template_filter('dateformat')
    def dateformat_filter(value, fmt='%d %b %Y'):
        if value:
            return value.strftime(fmt)
        return 'N/A'

    @app.context_processor
    def utility_processor():
        return dict(now=dt.datetime.now)

    with app.app_context():
        db.create_all()
        seed_data(app)

    return app

def seed_data(app):
    with app.app_context():
        if User.query.count() > 0:
            return

        admin = User(username='admin', email='admin@gym.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        trainer_user = User(username='trainer1', email='trainer1@gym.com', role='trainer')
        trainer_user.set_password('trainer123')
        db.session.add(trainer_user)

        member_user = User(username='member1', email='member1@gym.com', role='member')
        member_user.set_password('member123')
        db.session.add(member_user)
        db.session.flush()

        plans = [
            MembershipPlan(plan_name='Basic Monthly', duration=30, fees=999,
                           benefits='Gym floor access, Locker facility, Basic equipment'),
            MembershipPlan(plan_name='Standard Quarterly', duration=90, fees=2499,
                           benefits='All basic + Group classes, Nutrition consultation'),
            MembershipPlan(plan_name='Premium Annual', duration=365, fees=7999,
                           benefits='All standard + Personal trainer, Sauna, Pool'),
            MembershipPlan(plan_name='Student Plan', duration=30, fees=699,
                           benefits='Gym floor access, Weekdays only'),
        ]
        for p in plans:
            db.session.add(p)
        db.session.flush()

        trainer = Trainer(user_id=trainer_user.id, name='Rahul Sharma',
                          specialization='Strength Training, CrossFit',
                          contact_phone='9876543210', contact_email='rahul@gym.com',
                          bio='Certified trainer with 8 years experience.')
        t2 = Trainer(name='Priya Patel', specialization='Yoga, Zumba, Aerobics',
                     contact_phone='9876543211', contact_email='priya@gym.com',
                     bio='Yoga and aerobics expert.')
        t3 = Trainer(name='Amit Kumar', specialization='Boxing, MMA, Cardio',
                     contact_phone='9876543212', contact_email='amit@gym.com',
                     bio='Former national boxer.')
        db.session.add_all([trainer, t2, t3])
        db.session.flush()

        members_data = [
            ('Arjun Singh', 25, 'Male', '9111222333', 'arjun@email.com', 0),
            ('Sneha Gupta', 28, 'Female', '9222333444', 'sneha@email.com', 1),
            ('Vikram Rao', 32, 'Male', '9333444555', 'vikram@email.com', 2),
            ('Kavya Nair', 22, 'Female', '9444555666', 'kavya@email.com', 0),
            ('Rohit Mehta', 35, 'Male', '9555666777', 'rohit@email.com', 1),
            ('Anjali Sharma', 26, 'Female', '9666777888', 'anjali@email.com', 3),
        ]
        created_members = []
        for i, (name, age, gender, phone, email, plan_idx) in enumerate(members_data):
            plan = plans[plan_idx]
            join_date = date.today() - timedelta(days=i * 15)
            member = Member(
                name=name, age=age, gender=gender,
                contact=phone, email=email,
                join_date=join_date,
                health_details='No known conditions',
                plan_id=plan.id
            )
            if i == 0:
                member.user_id = member_user.id
            db.session.add(member)
            created_members.append((member, plan))
        db.session.flush()

        for member, plan in created_members:
            p = Payment(
                id=member.id,
                amount=plan.fees,
                payment_mode='UPI',
                status='Paid'
            )
            db.session.add(p)

        members_list = Member.query.all()
        for i in range(7):
            d = date.today() - timedelta(days=i)
            for m in members_list[:4]:
                a = Attendance(
                    id=m.id,
                    date=d,
                    check_in='06:30',
                    check_out='08:00'
                )
                db.session.add(a)

        schedules = [
            WorkoutSchedule(trainer_id=trainer.id,
                            workout_type='Weight Training',
                            time_slot='6:00 AM - 7:30 AM',
                            day_of_week='Mon, Wed, Fri'),
            WorkoutSchedule(trainer_id=t2.id,
                            workout_type='Yoga',
                            time_slot='7:00 AM - 8:00 AM',
                            day_of_week='Daily'),
            WorkoutSchedule(trainer_id=t2.id,
                            workout_type='Zumba',
                            time_slot='5:00 PM - 6:00 PM',
                            day_of_week='Tue, Thu, Sat'),
            WorkoutSchedule(trainer_id=t3.id,
                            workout_type='Boxing',
                            time_slot='6:00 PM - 7:30 PM',
                            day_of_week='Mon, Tue, Thu, Fri'),
        ]
        for s in schedules:
            db.session.add(s)

        db.session.commit()
        print("✅ Sample data seeded! Admin: admin/admin123")


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)