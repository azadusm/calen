from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta

def send_reminders():
    now = datetime.now()
    reminder_time = now + timedelta(hours=1)
    sessions = Session.query.filter(Session.start_time.between(now.time(), reminder_time.time()), Session.is_booked == True).all()

    for session in sessions:
        # Здесь вы можете интегрировать отправку сообщений пользователю через email/SMS/Telegram
        print(f"Напоминание: ваш сеанс начнется в {session.start_time}.")

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, 'interval', minutes=30)
scheduler.start()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import views, models
