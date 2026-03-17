import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gym-secret-key-2024'
    
    # ← Replace SQLite with MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/gym_management'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    WTF_CSRF_ENABLED = True