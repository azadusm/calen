from flask import render_template, request, redirect, url_for, jsonify, flash
from app import app, db
from .models import WorkSchedule, Holiday, Session, Booking
from datetime import datetime

@app.route('/admin/holiday/add', methods=['POST'])
def admin_add_holiday():
    name = request.form.get('name')
    date = request.form.get('date')
    if name and date:
        new_holiday = Holiday(name=name, date=date)
        db.session.add(new_holiday)
        db.session.commit()
        flash('Holiday added successfully!', 'success')
    else:
        flash('Please provide all required fields.', 'error')
    return redirect(url_for('admin_panel'))

@app.route('/admin/holiday/delete/<int:holiday_id>')
def admin_delete_holiday(holiday_id):
    holiday = Holiday.query.get_or_404(holiday_id)
    db.session.delete(holiday)
    db.session.commit()
    flash('Holiday deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/schedule/add', methods=['POST'])
def admin_add_schedule():
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    if start_time and end_time:
        new_schedule = WorkSchedule(start_time=start_time, end_time=end_time)
        db.session.add(new_schedule)
        db.session.commit()
        flash('Work schedule added successfully!', 'success')
    else:
        flash('Please provide all required fields.', 'error')
    return redirect(url_for('admin_panel'))

@app.route('/admin/schedule/delete/<int:schedule_id>')
def admin_delete_schedule(schedule_id):
    schedule = WorkSchedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Work schedule deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/schedule')
def schedule():
    work_schedule = WorkSchedule.query.all()
    holidays = Holiday.query.all()
    return render_template('schedule.html', work_schedule=work_schedule, holidays=holidays)

@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    day_of_week = request.form['day_of_week']
    start_time = datetime.strptime(request.form['start_time'], "%H:%M").time()
    end_time = datetime.strptime(request.form['end_time'], "%H:%M").time()

    schedule = WorkSchedule(day_of_week=day_of_week, start_time=start_time, end_time=end_time)
    db.session.add(schedule)
    db.session.commit()
    return redirect(url_for('schedule'))

@app.route('/add_holiday', methods=['POST'])
def add_holiday():
    holiday_date = datetime.strptime(request.form['holiday_date'], "%Y-%m-%d").date()
    name = request.form['name']

    holiday = Holiday(date=holiday_date, name=name)
    db.session.add(holiday)
    db.session.commit()
    return redirect(url_for('schedule'))

@app.route('/available_slots/<date>', methods=['GET'])
def available_slots(date):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()

    # Проверка на праздник
    holiday = Holiday.query.filter_by(date=date_obj).first()
    if holiday:
        return jsonify({"message": f"{holiday.name} - нерабочий день."})

    # Получение расписания
    day_of_week = date_obj.strftime("%A")
    schedule = WorkSchedule.query.filter_by(day_of_week=day_of_week).first()
    if not schedule:
        return jsonify({"message": "Нет расписания на этот день."})

    # Получение свободных слотов
    slots = Session.query.filter(Session.start_time >= schedule.start_time,
                                 Session.end_time <= schedule.end_time,
                                 Session.is_booked == False).all()
    return jsonify({"available_slots": [f"{slot.start_time} - {slot.end_time}" for slot in slots]})

@app.route('/book_slot', methods=['POST'])
def book_slot():
    data = request.get_json()
    date = data.get('date')
    slot = data.get('slot')

    # Преобразуем дату и время
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    start_time, end_time = [datetime.strptime(t.strip(), "%H:%M").time() for t in slot.split('-')]

    # Проверяем доступность слота
    session = Session.query.filter_by(date=date_obj, start_time=start_time, end_time=end_time, is_booked=False).first()
    if not session:
        return jsonify({"message": "Слот уже занят или недоступен."})

    # Бронируем слот
    session.is_booked = True
    db.session.commit()
    return jsonify({"message": "Слот успешно забронирован!"})

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete_session':
            session_id = request.form.get('session_id')
            session = Session.query.get(session_id)
            if session:
                db.session.delete(session)
                db.session.commit()

    sessions = Session.query.all()
    holidays = Holiday.query.all()
    return render_template('admin.html', sessions=sessions, holidays=holidays)

@app.route('/admin/bookings', methods=['GET', 'POST'])
def admin_bookings():
    date_filter = request.args.get('date')
    status_filter = request.args.get('status')
    
    query = Booking.query

    if date_filter:
        query = query.filter(db.func.date(Booking.timestamp) == date_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    bookings = query.all()

    return render_template('admin_bookings.html', bookings=bookings, date_filter=date_filter, status_filter=status_filter)
@app.route('/admin/statistics')
def admin_statistics():
    total_bookings = Booking.query.count()
    confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
    pending_bookings = Booking.query.filter_by(status='pending').count()

    return render_template('admin_statistics.html', 
                           total_bookings=total_bookings, 
                           confirmed_bookings=confirmed_bookings, 
                           pending_bookings=pending_bookings)

@app.route('/admin/booking/delete/<int:booking_id>')
def admin_delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('admin_bookings'))
@app.route('/admin/schedule/edit/<int:schedule_id>', methods=['GET', 'POST'])
def admin_edit_schedule(schedule_id):
    schedule = WorkSchedule.query.get_or_404(schedule_id)
    if request.method == 'POST':
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        if start_time and end_time:
            schedule.start_time = start_time
            schedule.end_time = end_time
            db.session.commit()
            flash('Schedule updated successfully!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Please provide valid data.', 'error')
    return render_template('edit_schedule.html', schedule=schedule)

@app.route('/admin/holiday/edit/<int:holiday_id>', methods=['GET', 'POST'])
def admin_edit_holiday(holiday_id):
    holiday = Holiday.query.get_or_404(holiday_id)
    if request.method == 'POST':
        name = request.form.get('name')
        date = request.form.get('date')
        if name and date:
            holiday.name = name
            holiday.date = date
            db.session.commit()
            flash('Holiday updated successfully!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Please provide valid data.', 'error')
    return render_template('edit_holiday.html', holiday=holiday)
