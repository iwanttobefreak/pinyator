from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Event, CastellTemplate, EventCastell, EventCastellAssignment, CastellPosition, User, Attendance, RoleDefaults

castells_bp = Blueprint('castells', __name__)


@castells_bp.route('/event/<int:event_id>/castells')
@login_required
def list_castells(event_id):
    event = Event.query.get_or_404(event_id)
    castells = EventCastell.query.filter_by(event_id=event_id).all()
    templates = CastellTemplate.query.all()
    return render_template('castell_list.html', event=event, castells=castells, templates=templates)


@castells_bp.route('/event/<int:event_id>/castells/afegir', methods=['POST'])
@login_required
def add_castell(event_id):
    if not current_user.is_cap():
        flash('No tens permís', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

    template_id = request.form.get('template_id')
    name = request.form.get('name', '')

    template = CastellTemplate.query.get_or_404(template_id)

    ec = EventCastell(
        event_id=event_id,
        template_id=template_id,
        name=name or template.display_name,
    )
    db.session.add(ec)
    db.session.commit()

    flash(f'Castell "{ec.name}" afegit', 'success')
    return redirect(url_for('castells.list_castells', event_id=event_id))


@castells_bp.route('/event/<int:event_id>/castell/<int:castell_id>')
@login_required
def edit_castell(event_id, castell_id):
    event = Event.query.get_or_404(event_id)
    ec = EventCastell.query.get_or_404(castell_id)

    if ec.event_id != event_id:
        flash('Castell no pertany a aquest event', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

    positions = CastellPosition.query.filter_by(template_id=ec.template_id).order_by(CastellPosition.y).all()
    assignments = {a.position_id: a for a in ec.assignments}

    going_ids = [a.user_id for a in Attendance.query.filter_by(event_id=event_id, status='va').all()]
    going_users = User.query.filter(User.id.in_(going_ids)).order_by(User.name).all() if going_ids else []

    assigned_ids = {a.user_id for a in ec.assignments if a.user_id}

    role_defaults = {rd.role: {'color': rd.color, 'text_color': rd.text_color, 'display_name': rd.display_name}
                     for rd in RoleDefaults.query.all()}

    return render_template(
        'castell_edit.html',
        event=event,
        ec=ec,
        positions=positions,
        assignments=assignments,
        going_users=going_users,
        assigned_ids=assigned_ids,
        role_defaults=role_defaults,
    )


@castells_bp.route('/event/<int:event_id>/castell/<int:castell_id>/assignar', methods=['POST'])
@login_required
def assign_position(event_id, castell_id):
    if not current_user.is_cap():
        return jsonify({'error': 'No tens permís'}), 403

    ec = EventCastell.query.get_or_404(castell_id)
    if ec.event_id != event_id:
        return jsonify({'error': 'Castell no pertany a aquest event'}), 400

    position_id = request.form.get('position_id')
    user_id = request.form.get('user_id')

    user_id = int(user_id) if user_id and user_id != '' else None

    assignment = EventCastellAssignment.query.filter_by(
        event_castell_id=castell_id, position_id=position_id
    ).first()

    if assignment:
        assignment.user_id = user_id
    else:
        assignment = EventCastellAssignment(
            event_castell_id=castell_id,
            position_id=position_id,
            user_id=user_id,
        )
        db.session.add(assignment)

    db.session.commit()
    return redirect(url_for('castells.edit_castell', event_id=event_id, castell_id=castell_id))


@castells_bp.route('/event/<int:event_id>/castell/<int:castell_id>/eliminar', methods=['POST'])
@login_required
def delete_castell(event_id, castell_id):
    if not current_user.is_cap():
        flash('No tens permís', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

    ec = EventCastell.query.get_or_404(castell_id)
    if ec.event_id != event_id:
        flash('Castell no pertany a aquest event', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

    db.session.delete(ec)
    db.session.commit()
    flash('Castell eliminat', 'success')
    return redirect(url_for('castells.list_castells', event_id=event_id))
