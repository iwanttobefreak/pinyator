from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Event, Attendance, User, EventCastell

events_bp = Blueprint('events', __name__)


@events_bp.route('/')
@login_required
def list_events():
    events = Event.query.order_by(Event.date.desc()).all()
    attendances = Attendance.query.filter_by(user_id=current_user.id).all()
    attendance_map = {a.event_id: a.status for a in attendances}
    return render_template('events.html', events=events, attendance_map=attendance_map)


def _parse_date(date_str, time_str):
    for fmt in ('%d/%m/%Y %H:%M', '%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(f'{date_str} {time_str}', fmt)
        except ValueError:
            continue
    return None


@events_bp.route('/event/nou', methods=['GET', 'POST'])
@login_required
def create_event():
    if not current_user.is_cap():
        flash('No tens permís per crear events', 'error')
        return redirect(url_for('events.list_events'))

    if request.method == 'POST':
        title = request.form.get('title')
        date_str = request.form.get('date')
        time_str = request.form.get('time', '20:00')
        event_type = request.form.get('type')
        description = request.form.get('description', '')

        date = _parse_date(date_str, time_str)
        if not date:
            flash('Format de data incorrecte', 'error')
            return render_template('event_form.html', event=None)

        event = Event(
            title=title,
            date=date,
            type=event_type,
            description=description,
        )
        db.session.add(event)
        db.session.commit()

        flash('Event creat correctament', 'success')
        return redirect(url_for('events.list_events'))

    return render_template('event_form.html', event=None)


@events_bp.route('/event/<int:event_id>')
@login_required
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    attendances = Attendance.query.filter_by(event_id=event_id).all()

    attendance_map = {a.user_id: a.status for a in attendances}

    count_va = sum(1 for a in attendances if a.status == 'va')
    count_no_va = sum(1 for a in attendances if a.status == 'no_va')
    count_no_ho_sap = sum(1 for a in attendances if a.status == 'no_ho_sap')

    users = User.query.order_by(User.name).all()
    castells = EventCastell.query.filter_by(event_id=event_id).all()

    return render_template(
        'event_detail.html',
        event=event,
        users=users,
        attendance_map=attendance_map,
        count_va=count_va,
        count_no_va=count_no_va,
        count_no_ho_sap=count_no_ho_sap,
        castells=castells,
    )


@events_bp.route('/event/<int:event_id>/editar', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.is_cap():
        flash('No tens permís per editar events', 'error')
        return redirect(url_for('events.list_events'))

    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form.get('title')
        date_str = request.form.get('date')
        time_str = request.form.get('time', '20:00')
        event.type = request.form.get('type')
        event.description = request.form.get('description', '')

        date = _parse_date(date_str, time_str)
        if not date:
            flash('Format de data incorrecte', 'error')
            return render_template('event_form.html', event=event)
        event.date = date

        db.session.commit()
        flash('Event actualitzat correctament', 'success')
        return redirect(url_for('events.event_detail', event_id=event.id))

    return render_template('event_form.html', event=event)
