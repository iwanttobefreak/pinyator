from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Event, Attendance

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/event/<int:event_id>/assistencia', methods=['POST'])
@login_required
def set_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    status = request.form.get('status')

    if status not in ('va', 'no_va', 'no_ho_sap'):
        flash('Estat no vàlid', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

    attendance = Attendance.query.filter_by(
        user_id=current_user.id, event_id=event_id
    ).first()

    if attendance:
        attendance.status = status
    else:
        attendance = Attendance(
            user_id=current_user.id,
            event_id=event_id,
            status=status,
        )
        db.session.add(attendance)

    db.session.commit()
    flash('Assistència registrada', 'success')
    return redirect(url_for('events.event_detail', event_id=event_id))


@attendance_bp.route('/event/<int:event_id>/assistencia/<int:user_id>', methods=['POST'])
@login_required
def set_attendance_admin(event_id, user_id):
    if not current_user.is_cap():
        flash('No tens permís', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

    status = request.form.get('status')

    if status not in ('va', 'no_va', 'no_ho_sap'):
        flash('Estat no vàlid', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

    attendance = Attendance.query.filter_by(
        user_id=user_id, event_id=event_id
    ).first()

    if attendance:
        attendance.status = status
    else:
        attendance = Attendance(
            user_id=user_id,
            event_id=event_id,
            status=status,
        )
        db.session.add(attendance)

    db.session.commit()
    flash('Assistència actualitzada', 'success')
    return redirect(url_for('events.event_detail', event_id=event_id))
