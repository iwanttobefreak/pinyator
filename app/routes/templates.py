import time
import unicodedata
from werkzeug.security import generate_password_hash

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import CastellTemplate, CastellPosition, RoleDefaults, User

templates_bp = Blueprint('templates_admin', __name__, url_prefix='/admin/templates')


@templates_bp.route('')
@login_required
def list_templates():
    if not current_user.is_admin():
        flash('No tens permís', 'error')
        return redirect(url_for('events.list_events'))

    templates = CastellTemplate.query.order_by(CastellTemplate.name).all()
    return render_template('admin/templates.html', templates=templates)


@templates_bp.route('/nou', methods=['GET', 'POST'])
@login_required
def create_template():
    if not current_user.is_admin():
        flash('No tens permís', 'error')
        return redirect(url_for('events.list_events'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()

        if not name or not display_name:
            flash('Nom i display_name són obligatoris', 'error')
            return render_template('admin/template_form.html', template=None)

        if CastellTemplate.query.filter_by(name=name).first():
            flash('Ja existeix una plantilla amb aquest nom', 'error')
            return render_template('admin/template_form.html', template=None)

        t = CastellTemplate(name=name, display_name=display_name)
        db.session.add(t)
        db.session.commit()
        flash('Plantilla creada', 'success')
        return redirect(url_for('templates_admin.list_templates'))

    return render_template('admin/template_form.html', template=None)


@templates_bp.route('/<int:tid>/editar', methods=['GET', 'POST'])
@login_required
def edit_template(tid):
    if not current_user.is_admin():
        flash('No tens permís', 'error')
        return redirect(url_for('events.list_events'))

    t = CastellTemplate.query.get_or_404(tid)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()

        if not name or not display_name:
            flash('Nom i display_name són obligatoris', 'error')
            return render_template('admin/template_form.html', template=t)

        existing = CastellTemplate.query.filter_by(name=name).first()
        if existing and existing.id != tid:
            flash('Ja existeix una plantilla amb aquest nom', 'error')
            return render_template('admin/template_form.html', template=t)

        t.name = name
        t.display_name = display_name
        db.session.commit()
        flash('Plantilla actualitzada', 'success')
        return redirect(url_for('templates_admin.list_templates'))

    return render_template('admin/template_form.html', template=t)


@templates_bp.route('/<int:tid>/eliminar', methods=['POST'])
@login_required
def delete_template(tid):
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403

    t = CastellTemplate.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    flash('Plantilla eliminada', 'success')
    return redirect(url_for('templates_admin.list_templates'))


@templates_bp.route('/<int:tid>/exportar')
@login_required
def export_template(tid):
    if not current_user.is_admin():
        flash('No tens permís', 'error')
        return redirect(url_for('events.list_events'))

    t = CastellTemplate.query.get_or_404(tid)
    data = {
        'name': t.name,
        'display_name': t.display_name,
        'positions': [
            {
                'name': p.name,
                'label': p.label,
                'role': p.role,
                'x': p.x,
                'y': p.y,
                'w': p.w,
                'h': p.h,
                'angle': p.angle,
                'shape': p.shape,
                'color': p.color,
                'text_color': p.text_color,
            }
            for p in CastellPosition.query.filter_by(template_id=tid).order_by(CastellPosition.name).all()
        ],
    }
    import json
    resp = jsonify(data)
    resp.headers['Content-Disposition'] = f'attachment; filename="{t.name}.json"'
    return resp


@templates_bp.route('/importar', methods=['POST'])
@login_required
def import_template():
    if not current_user.is_admin():
        flash('No tens permís', 'error')
        return redirect(url_for('events.list_events'))

    file = request.files.get('fitxer')
    if not file:
        flash('No s\'ha rebut cap fitxer', 'error')
        return redirect(url_for('templates_admin.list_templates'))

    import json
    try:
        data = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError):
        flash('El fitxer no és un JSON vàlid', 'error')
        return redirect(url_for('templates_admin.list_templates'))

    name = data.get('name', '').strip()
    display_name = data.get('display_name', '').strip()
    if not name or not display_name:
        flash('El JSON ha de contenir "name" i "display_name"', 'error')
        return redirect(url_for('templates_admin.list_templates'))

    existing = CastellTemplate.query.filter_by(name=name).first()
    if existing:
        flash(f'Ja existeix una plantilla amb el nom "{name}"', 'error')
        return redirect(url_for('templates_admin.list_templates'))

    t = CastellTemplate(name=name, display_name=display_name)
    db.session.add(t)
    db.session.flush()

    for pos in data.get('positions', []):
        db.session.add(CastellPosition(
            template_id=t.id,
            name=pos.get('name', 'posicio'),
            label=pos.get('label', 'Posició'),
            role=pos.get('role', 'baix'),
            x=int(pos.get('x', 0)),
            y=int(pos.get('y', 0)),
            w=int(pos.get('w', 80)),
            h=int(pos.get('h', 30)),
            angle=int(pos.get('angle', 0)),
            shape=int(pos.get('shape', 0)),
            color=pos.get('color', None),
            text_color=pos.get('text_color', None),
        ))

    db.session.commit()
    flash(f'Plantilla "{display_name}" importada correctament', 'success')
    return redirect(url_for('templates_admin.list_templates'))


@templates_bp.route('/<int:tid>')
@login_required
def editor(tid):
    if not current_user.is_admin():
        flash('No tens permís', 'error')
        return redirect(url_for('events.list_events'))

    t = CastellTemplate.query.get_or_404(tid)
    positions = CastellPosition.query.filter_by(template_id=tid).order_by(CastellPosition.name).all()

    roles = [
        'acotxador', 'agulla', 'baix', 'contrafort', 'crossa',
        'dos', 'enxaneta', 'lateral', 'pinya', 'primera',
        'quart', 'quint', 'segon', 'sisè', 'setè',
        'terç', 'vent',
    ]

    role_defaults = {rd.role: {'color': rd.color, 'text_color': rd.text_color, 'display_name': rd.display_name}
                     for rd in RoleDefaults.query.all()}

    shapes = [
        (0, 'Rectangle'),
        (1, 'Oval'),
        (2, 'Trapezi esq'),
        (3, 'Trapezi dre'),
        (4, 'Triangle'),
        (5, 'Paral·lelogram dret'),
        (6, 'Paral·lelogram esq'),
        (7, 'Trapezi ample'),
    ]

    return render_template('admin/template_edit.html',
                           template=t, positions=positions,
                           roles=roles, shapes=shapes,
                           role_defaults=role_defaults)


@templates_bp.route('/<int:tid>/posicions', methods=['POST'])
@login_required
def add_position(tid):
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403

    t = CastellTemplate.query.get_or_404(tid)
    data = request.get_json(silent=True) or request.form

    role = data.get('role', 'baix')
    role_def = RoleDefaults.query.filter_by(role=role).first()
    default_color = role_def.color if role_def else '#cfe2f3'
    default_text_color = role_def.text_color if role_def else None

    p = CastellPosition(
        template_id=tid,
        name=data.get('name', 'nova'),
        label=data.get('label', 'Nova'),
        role=role,
        x=int(data.get('x', 100)),
        y=int(data.get('y', 100)),
        w=int(data.get('w', 80)),
        h=int(data.get('h', 30)),
        angle=int(data.get('angle', 0)),
        shape=int(data.get('shape', 0)),
        color=data.get('color', None) or default_color,
        text_color=data.get('text_color', None) or default_text_color,
    )
    db.session.add(p)
    db.session.commit()

    if request.is_json:
        return jsonify({'id': p.id, 'name': p.name})

    flash('Posició afegida', 'success')
    return redirect(url_for('templates_admin.editor', tid=tid))


@templates_bp.route('/<int:tid>/posicions/<int:pid>', methods=['POST'])
@login_required
def update_position(tid, pid):
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403

    CastellTemplate.query.get_or_404(tid)
    p = CastellPosition.query.get_or_404(pid)

    if p.template_id != tid:
        return jsonify({'error': 'No pertany a aquesta plantilla'}), 400

    data = request.get_json(silent=True) or request.form

    p.name = data.get('name', p.name)
    p.label = data.get('label', p.label)
    p.role = data.get('role', p.role)
    p.x = int(data.get('x', p.x))
    p.y = int(data.get('y', p.y))
    p.w = int(data.get('w', p.w))
    p.h = int(data.get('h', p.h))
    p.angle = int(data.get('angle', p.angle))
    p.shape = int(data.get('shape', p.shape))
    p.color = data.get('color', p.color) or None
    p.text_color = data.get('text_color', p.text_color) or None

    db.session.commit()

    if request.is_json:
        return jsonify({'ok': True})

    flash('Posició actualitzada', 'success')
    return redirect(url_for('templates_admin.editor', tid=tid))


@templates_bp.route('/<int:tid>/posicions/<int:pid>/eliminar', methods=['POST'])
@login_required
def delete_position(tid, pid):
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403

    CastellTemplate.query.get_or_404(tid)
    p = CastellPosition.query.get_or_404(pid)

    if p.template_id != tid:
        return jsonify({'error': 'No pertany a aquesta plantilla'}), 400

    db.session.delete(p)
    db.session.commit()

    if request.is_json:
        return jsonify({'ok': True})

    flash('Posició eliminada', 'success')
    return redirect(url_for('templates_admin.editor', tid=tid))


@templates_bp.route('/<int:tid>/posicions/<int:pid>/duplicar', methods=['POST'])
@login_required
def duplicate_position(tid, pid):
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403

    CastellTemplate.query.get_or_404(tid)
    orig = CastellPosition.query.get_or_404(pid)

    if orig.template_id != tid:
        return jsonify({'error': 'No pertany a aquesta plantilla'}), 400

    new_p = CastellPosition(
        template_id=tid,
        name=orig.name + '_copia',
        label=orig.label,
        role=orig.role,
        x=orig.x + 25,
        y=orig.y + 25,
        w=orig.w,
        h=orig.h,
        angle=orig.angle,
        shape=orig.shape,
        color=orig.color,
        text_color=orig.text_color,
    )
    db.session.add(new_p)
    db.session.commit()

    return jsonify({
        'id': new_p.id,
        'name': new_p.name,
        'label': new_p.label,
        'role': new_p.role,
        'x': new_p.x,
        'y': new_p.y,
        'w': new_p.w,
        'h': new_p.h,
        'angle': new_p.angle,
        'shape': new_p.shape,
        'color': new_p.color or '',
        'text_color': new_p.text_color or '',
    })


@templates_bp.route('/configuracio')
@login_required
def config():
    if not current_user.is_admin():
        flash('No tens permís', 'error')
        return redirect(url_for('events.list_events'))
    role_defaults = RoleDefaults.query.order_by(RoleDefaults.role).all()
    return render_template('admin/configuracio.html', role_defaults=role_defaults)


@templates_bp.route('/configuracio/afegir', methods=['POST'])
@login_required
def config_add_role():
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403
    role = request.form.get('role', '').strip()
    display_name = request.form.get('display_name', '').strip()
    color = request.form.get('color', '#cfe2f3').strip()
    text_color = request.form.get('text_color', '').strip() or None
    if not role or not display_name:
        flash('Nom i display_name obligatoris', 'error')
        return redirect(url_for('templates_admin.config'))
    if RoleDefaults.query.filter_by(role=role).first():
        flash('Aquest rol ja existeix', 'error')
        return redirect(url_for('templates_admin.config'))
    db.session.add(RoleDefaults(role=role, display_name=display_name, color=color, text_color=text_color))
    db.session.commit()
    flash('Rol afegit', 'success')
    return redirect(url_for('templates_admin.config'))


@templates_bp.route('/configuracio/<int:rid>', methods=['POST'])
@login_required
def config_update_role(rid):
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403
    rd = RoleDefaults.query.get_or_404(rid)
    rd.color = request.form.get('color', rd.color)
    rd.text_color = request.form.get('text_color', '').strip() or None
    db.session.commit()
    flash('Configuració actualitzada', 'success')
    return redirect(url_for('templates_admin.config'))


@templates_bp.route('/configuracio/<int:rid>/eliminar', methods=['POST'])
@login_required
def config_delete_role(rid):
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403
    rd = RoleDefaults.query.get_or_404(rid)
    db.session.delete(rd)
    db.session.commit()
    flash('Rol eliminat', 'success')
    return redirect(url_for('templates_admin.config'))


def _slug(name):
    s = name.lower().strip()
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if unicodedata.category(c) != 'Mn')
    s = ''.join(c for c in s if c.isalnum() or c in ' ._-')
    s = s.replace(' ', '.').replace('..', '.').strip('._-')
    return s if s else 'casteller'


@templates_bp.route('/configuracio/usuaris')
@login_required
def config_users():
    if not current_user.is_admin():
        flash('No tens permís', 'error')
        return redirect(url_for('events.list_events'))
    users = User.query.order_by(User.name).all()
    return render_template('admin/usuaris.html', users=users)


@templates_bp.route('/configuracio/usuaris/importar', methods=['POST'])
@login_required
def config_import_users():
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403

    filepath = '/tmp/usuaris.txt'
    try:
        with open(filepath) as f:
            names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        flash(f'No es troba el fitxer {filepath}', 'error')
        return redirect(url_for('templates_admin.config_users'))

    # Delete existing castellers
    for attempt in range(5):
        try:
            User.query.filter_by(role='casteller').delete()
            db.session.flush()
            break
        except Exception:
            db.session.rollback()
            time.sleep(1)

    count = 0
    for name in names:
        username = _slug(name)
        if User.query.filter_by(username=username).first():
            continue
        user = User(
            username=username,
            password_hash=generate_password_hash(username),
            name=name,
            full_name=name,
            role='casteller',
        )
        db.session.add(user)
        count += 1

    for attempt in range(5):
        try:
            db.session.commit()
            break
        except Exception:
            db.session.rollback()
            time.sleep(1)

    flash(f'Importats {count} castellers', 'success')
    return redirect(url_for('templates_admin.config_users'))


@templates_bp.route('/configuracio/usuaris/nou', methods=['POST'])
@login_required
def config_add_user():
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403

    name = request.form.get('name', '').strip()
    username = _slug(request.form.get('username', '').strip() or name)
    password = request.form.get('password', '').strip() or username

    if not name:
        flash('El nom és obligatori', 'error')
        return redirect(url_for('templates_admin.config_users'))

    if User.query.filter_by(username=username).first():
        flash(f'L\'usuari "{username}" ja existeix', 'error')
        return redirect(url_for('templates_admin.config_users'))

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        name=name,
        full_name=name,
        role='casteller',
    )
    db.session.add(user)
    db.session.commit()
    flash(f'Usuari "{name}" creat (usuari: {username}, contrasenya: {password})', 'success')
    return redirect(url_for('templates_admin.config_users'))


@templates_bp.route('/configuracio/usuaris/<int:uid>/reset-password', methods=['POST'])
@login_required
def config_reset_password(uid):
    if not current_user.is_admin():
        return jsonify({'error': 'No tens permís'}), 403

    user = User.query.get_or_404(uid)
    new_password = request.form.get('password', '').strip() or user.username
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash(f'Contrasenya reinicialitzada per "{user.name}" (usuari: {user.username}, contrasenya: {new_password})', 'success')
    return redirect(url_for('templates_admin.config_users'))
