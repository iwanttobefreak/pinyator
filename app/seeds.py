import unicodedata
import random
from datetime import datetime
from werkzeug.security import generate_password_hash

from app import db
from app.models import User, Event, Attendance, CastellTemplate, CastellPosition, EventCastell, RoleDefaults


SOBRENOMS = [
    'Tronxo', 'Xicot', 'Nan', 'Gros', 'Pesat', 'Llarg', 'Baixet', 'Ràpid',
    'Forn', 'Pedra', 'Tronc', 'Maça', 'Pal', 'Roca', 'Ferro', 'Acer',
    'Pi', 'Roure', 'Alzina', 'Faig', 'Poll', 'Plàtan', 'Om', 'Freixe',
    'Vent', 'Núvol', 'Llamp', 'Tro', 'Sol', 'Lluna', 'Estel', 'Cel',
    'Mar', 'Riu', 'Font', 'Llac', 'Puig', 'Serra', 'Roc', 'Cingle',
    'Gos', 'Gat', 'Òliba', 'Falcó', 'Àliga', 'Colom', 'Corb', 'Mussol',
    'Teixó', 'Esquirol', 'Conill', 'Guineu', 'Cabró', 'Bou', 'Vaca', 'Toro',
    'Castor', 'Llebre', 'Tortuga', 'Cargol', 'Granota', 'Salmó', 'Truita', 'Anguila',
    'POM', 'Xampú', 'Xàndal', 'Gínjol', 'Nyam', 'Carxofa', 'Espinac', 'Col',
    'Cirera', 'Poma', 'Perà', 'Préssec', 'Plàtan', 'Raïm', 'Figa', 'Nou',
    'Fresa', 'Maduixa', 'Mora', 'Gerds', 'Llimona', 'Taronja', 'Mandarina', 'Síndria',
    'Cava', 'Vi', 'Cervesa', 'Rum', 'Ginebra', 'Vermut', 'Ponx', 'Licor',
    'Pa', 'Coca', 'Pastís', 'Brioix', 'Galeta', 'Bunyol', 'Torrada', 'Cereal',
]

NOMS_CATALANS = [
    'Marc', 'Jan', 'Pol', 'Èric', 'Arnau', 'Pau', 'Alex', 'Hugo', 'Nil', 'Martí',
    'Biel', 'Joan', 'Laia', 'Maria', 'Julia', 'Martina', 'Emma', 'Ona', 'Sofia', 'Clàudia',
    'Marta', 'Carla', 'Sara', 'Paula', 'Joana', 'Anna', 'Elena', 'Laura', 'Irene', 'Cristina',
    'Pere', 'Josep', 'Antoni', 'Manel', 'Ramon', 'Lluís', 'Jordi', 'Albert', 'David', 'Carles',
    'Xavier', 'Jaume', 'Sergi', 'Oriol', 'Àlex', 'Víctor', 'Miquel', 'Joaquim', 'Felip', 'Andreu',
    'Rosa', 'Montse', 'Dolors', 'Neus', 'Pilar', 'Remei', 'Núria', 'Carme', 'Ester', 'Mercè',
    'Helena', 'Judit', 'Mariona', 'Mireia', 'Alba', 'Ariadna', 'Bet', 'Celia', 'Diana', 'Georgina',
    'Àngel', 'Bernat', 'Climent', 'Domènec', 'Esteve', 'Ferran', 'Guillem', 'Hèctor', 'Ignasi', 'Lluc',
    'Aleix', 'Blai', 'Cebrià', 'Dalmau', 'Eloi', 'Fèlix', 'Guerau', 'Heribert', 'Isidre', 'Llàtzer',
    'Neus', 'Olga', 'Pilar', 'Queralt', 'Remei', 'Sònia', 'Trini', 'Urbana', 'Viviana', 'Wendy',
]

POSITION_DISTRIBUTION = {
    'baix': 15, 'segon': 14, 'terç': 12, 'quart': 10, 'quint': 8,
    'sisè': 7, 'setè': 5, 'dos': 5, 'acotxador': 5, 'enxaneta': 5,
    'vent': 6, 'lateral': 4, 'crossa': 4,
}

HEIGHT_RANGES = {
    'enxaneta': (140, 155), 'acotxador': (150, 165), 'dos': (155, 170),
    'setè': (160, 175), 'sisè': (162, 176), 'quint': (165, 178),
    'quart': (168, 182), 'terç': (170, 185), 'segon': (172, 188),
    'baix': (175, 195), 'vent': (170, 190), 'lateral': (170, 190),
    'crossa': (170, 190),
}

ARM_RANGES = {
    'enxaneta': (55, 65), 'acotxador': (60, 70), 'dos': (60, 72),
    'setè': (65, 75), 'sisè': (65, 76), 'quint': (68, 78),
    'quart': (70, 82), 'terç': (72, 85), 'segon': (75, 88),
    'baix': (78, 95), 'vent': (75, 90), 'lateral': (75, 90),
    'crossa': (75, 90),
}

COGNOMS = [
    'Garcia', 'Martínez', 'López', 'Sánchez', 'Fernández',
    'Puig', 'Serra', 'Ferrer', 'Costa', 'Roca',
    'Casals', 'Prat', 'Soler', 'Vila', 'Rovira',
    'Pons', 'Vidal', 'Font', 'Mestre', 'Sala',
    'Bosch', 'Comas', 'Camps', 'Cervera', 'Pujol',
    'Torres', 'Estrada', 'Llobet', 'Pagès', 'Pi',
]


DEFAULT_ROLES = [
    ('agulla', 'Agulla', '#f3ff27', None),
    ('baix', 'Baix', '#9548fd', '#ffffff'),
    ('contrafort', 'Contrafort', '#754e7f', '#ffffff'),
    ('crossa', 'Crossa', '#35ffa0', None),
    ('lateral', 'Lateral', '#95d0ff', None),
    ('pinya', 'Pinya', '#9bffc3', None),
    ('primera', 'Primera', '#ffd3a3', None),
    ('vent', 'Vent', '#ffa3ad', None),
    ('acotxador', 'Acotxador', '#c9daf8', None),
    ('dos', 'Dos', '#b6d7a8', None),
    ('enxaneta', 'Enxaneta', '#a2c4c9', None),
    ('quart', 'Quart', '#f4cccc', None),
    ('quint', 'Quint', '#d0e0e3', None),
    ('segon', 'Segon', '#d9ead3', None),
    ('setè', 'Setè', '#ead1dc', None),
    ('sisè', 'Sisè', '#ead1dc', None),
    ('terç', 'Terç', '#fff2cc', None),
]

def _seed_role_defaults():
    if RoleDefaults.query.first():
        return
    for role, display_name, color, text_color in DEFAULT_ROLES:
        db.session.add(RoleDefaults(
            role=role, display_name=display_name,
            color=color, text_color=text_color,
        ))
    db.session.commit()

def seed_all():
    _seed_users()
    _seed_templates()
    _seed_role_defaults()
    _seed_test_event()


def _slug(name):
    s = name.lower().strip()
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if unicodedata.category(c) != 'Mn')
    s = ''.join(c for c in s if c.isalnum() or c in ' ._-')
    s = s.replace(' ', '.').replace('..', '.').strip('._-')
    return s if s else 'casteller'


def _import_usuaris(filepath='/tmp/usuaris.txt'):
    try:
        with open(filepath) as f:
            names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return None
    users = []
    seen = set()
    for name in names:
        username = _slug(name)
        if username in seen or User.query.filter_by(username=username).first():
            continue
        seen.add(username)
        user = User(
            username=username,
            password_hash=generate_password_hash(username),
            name=name,
            full_name=name,
            role='casteller',
        )
        users.append(user)
    return users


def _seed_users():
    if User.query.count() > 10:
        return

    users = []

    admin = User(
        username='admin', name='Administrador',
        full_name='Administrador del Sistema', role='admin',
        position='baix', height=180, arm_height=85,
    )
    admin.password_hash = generate_password_hash('admin')
    users.append(admin)

    cap = User(
        username='cap', name='Cap de Colla',
        full_name='Cap de Colla', role='cap',
        position='baix', height=185, arm_height=88,
    )
    cap.password_hash = generate_password_hash('cap')
    users.append(cap)

    imported = _import_usuaris()
    if imported:
        users.extend(imported)
    else:
        used_sobrenoms = set()
        used_noms = set()
        used_sobrenoms.update(['admin', 'cap'])
        used_noms.update(['Administrador del Sistema', 'Cap de Colla'])

        pos_pool = []
        for pos, count in POSITION_DISTRIBUTION.items():
            pos_pool.extend([pos] * count)
        random.shuffle(pos_pool)

        for i in range(100):
            sobrenom = random.choice(SOBRENOMS)
            while sobrenom in used_sobrenoms:
                sobrenom = random.choice(SOBRENOMS)
            used_sobrenoms.add(sobrenom)

            nom = random.choice(NOMS_CATALANS)
            cognom = random.choice(COGNOMS)
            full_name = f'{nom} {cognom}'
            while full_name in used_noms:
                nom = random.choice(NOMS_CATALANS)
                full_name = f'{nom} {cognom}'
            used_noms.add(full_name)

            pos = pos_pool[i % len(pos_pool)]
            h_min, h_max = HEIGHT_RANGES[pos]
            a_min, a_max = ARM_RANGES[pos]
            height = random.randint(h_min, h_max)
            arm_height = random.randint(a_min, a_max)

            user = User(
                username=sobrenom.lower(),
                name=sobrenom,
                full_name=full_name,
                role='casteller',
                position=pos,
                height=height,
                arm_height=arm_height,
                photo=f'https://ui-avatars.com/api/?name={sobrenom}&background=8B0000&color=fff&size=200',
            )
            user.password_hash = generate_password_hash('pinyator')
            users.append(user)

    db.session.add_all(users)
    db.session.commit()


ROLE_COLORS = {
    'agulla': '#f3ff27', 'baix': '#9548fd', 'contrafort': '#754e7f',
    'crossa': '#35ffa0', 'lateral': '#95d0ff', 'pinya': '#9bffc3',
    'primera': '#ffd3a3', 'vent': '#ffa3ad',
}

def _pos(name, label, role, x, y, w=80, h=30, angle=0):
    color = ROLE_COLORS.get(role, '#cfe2f3')
    text_color = '#ffffff' if role in ('baix', 'contrafort') else None
    return (name, label, role, x, y, w, h, angle, color, text_color)


P4_POS = [
    _pos('enxaneta', 'Enxaneta', 'enxaneta', 370, 130, 60, 25),
    _pos('acotxador', 'Acotxador', 'acotxador', 370, 170, 60, 25),
    _pos('segon', 'Segon', 'segon', 370, 210, 60, 25),
    _pos('baix', 'Baix', 'baix', 370, 250, 60, 25),
]

P5_POS = [
    _pos('enxaneta', 'Enxaneta', 'enxaneta', 370, 100, 60, 25),
    _pos('acotxador', 'Acotxador', 'acotxador', 370, 135, 60, 25),
    _pos('dos', 'Dos', 'dos', 370, 170, 60, 25),
    _pos('segon', 'Segon', 'segon', 370, 205, 60, 25),
    _pos('baix', 'Baix', 'baix', 370, 240, 60, 25),
]

T2D6_POS = [
    _pos('enxaneta', 'Enxaneta', 'enxaneta', 370, 50, 60, 25),
    _pos('acotxador', 'Acotxador', 'acotxador', 370, 80, 60, 25),
    _pos('dos_1', 'Dos (esq)', 'dos', 340, 110, 55, 25),
    _pos('dos_2', 'Dos (dre)', 'dos', 400, 110, 55, 25),
    _pos('quint_1', 'Quint (esq)', 'quint', 325, 145, 50, 25),
    _pos('quint_2', 'Quint (dre)', 'quint', 395, 145, 50, 25),
    _pos('quart_1', 'Quart (esq)', 'quart', 325, 180, 50, 25),
    _pos('quart_2', 'Quart (dre)', 'quart', 395, 180, 50, 25),
    _pos('terç_1', 'Terç (esq)', 'terç', 325, 215, 50, 25),
    _pos('terç_2', 'Terç (dre)', 'terç', 395, 215, 50, 25),
    _pos('segon_1', 'Segon (esq)', 'segon', 325, 250, 50, 25),
    _pos('segon_2', 'Segon (dre)', 'segon', 395, 250, 50, 25),
    _pos('baix_1', 'Baix (esq)', 'baix', 325, 285, 50, 25),
    _pos('baix_2', 'Baix (dre)', 'baix', 395, 285, 50, 25),
    _pos('primera', 'Primera', 'primera', 360, 330, 80, 25),
    _pos('vent_1', 'Vent esq', 'vent', 230, 160, 65, 25, -30),
    _pos('vent_2', 'Vent dre', 'vent', 470, 160, 65, 25, 30),
    _pos('lateral_1', 'Lateral esq', 'lateral', 240, 240, 60, 25, -20),
    _pos('lateral_2', 'Lateral dre', 'lateral', 480, 240, 60, 25, 20),
    _pos('crossa', 'Crossa', 'crossa', 360, 355, 80, 25),
]

T2D6N_POS = [
    _pos('enxaneta', 'Enxaneta', 'enxaneta', 370, 50, 60, 25),
    _pos('acotxador', 'Acotxador', 'acotxador', 370, 80, 60, 25),
    _pos('dos_1', 'Dos (esq)', 'dos', 340, 110, 55, 25),
    _pos('dos_2', 'Dos (dre)', 'dos', 400, 110, 55, 25),
    _pos('quint_1', 'Quint (esq)', 'quint', 325, 145, 50, 25),
    _pos('quint_2', 'Quint (dre)', 'quint', 395, 145, 50, 25),
    _pos('quart_1', 'Quart (esq)', 'quart', 325, 180, 50, 25),
    _pos('quart_2', 'Quart (dre)', 'quart', 395, 180, 50, 25),
    _pos('terç_1', 'Terç (esq)', 'terç', 325, 215, 50, 25),
    _pos('terç_2', 'Terç (dre)', 'terç', 395, 215, 50, 25),
    _pos('segon_1', 'Segon (esq)', 'segon', 325, 250, 50, 25),
    _pos('segon_2', 'Segon (dre)', 'segon', 395, 250, 50, 25),
    _pos('baix_1', 'Baix (esq)', 'baix', 325, 285, 50, 25),
    _pos('baix_2', 'Baix (dre)', 'baix', 395, 285, 50, 25),
    _pos('vent_1', 'Vent esq', 'vent', 230, 160, 65, 25, -30),
    _pos('vent_2', 'Vent dre', 'vent', 470, 160, 65, 25, 30),
    _pos('lateral_1', 'Lateral esq', 'lateral', 240, 240, 60, 25, -20),
    _pos('lateral_2', 'Lateral dre', 'lateral', 480, 240, 60, 25, 20),
]

T3D6_POS = [
    _pos('enxaneta', 'Enxaneta', 'enxaneta', 370, 40, 60, 25),
    _pos('acotxador', 'Acotxador', 'acotxador', 370, 70, 60, 25),
    _pos('dos_1', 'Dos (esq)', 'dos', 340, 100, 55, 25),
    _pos('dos_2', 'Dos (dre)', 'dos', 400, 100, 55, 25),
    _pos('quint_1', 'Quint (esq)', 'quint', 310, 130, 47, 25),
    _pos('quint_2', 'Quint (cen)', 'quint', 370, 130, 47, 25),
    _pos('quint_3', 'Quint (dre)', 'quint', 430, 130, 47, 25),
    _pos('quart_1', 'Quart (esq)', 'quart', 310, 160, 47, 25),
    _pos('quart_2', 'Quart (cen)', 'quart', 370, 160, 47, 25),
    _pos('quart_3', 'Quart (dre)', 'quart', 430, 160, 47, 25),
    _pos('terç_1', 'Terç (esq)', 'terç', 310, 190, 47, 25),
    _pos('terç_2', 'Terç (cen)', 'terç', 370, 190, 47, 25),
    _pos('terç_3', 'Terç (dre)', 'terç', 430, 190, 47, 25),
    _pos('segon_1', 'Segon (esq)', 'segon', 310, 220, 47, 25),
    _pos('segon_2', 'Segon (cen)', 'segon', 370, 220, 47, 25),
    _pos('segon_3', 'Segon (dre)', 'segon', 430, 220, 47, 25),
    _pos('baix_1', 'Baix (esq)', 'baix', 310, 250, 47, 25),
    _pos('baix_2', 'Baix (cen)', 'baix', 370, 250, 47, 25),
    _pos('baix_3', 'Baix (dre)', 'baix', 430, 250, 47, 25),
    _pos('primera_1', 'Primera (esq)', 'primera', 320, 300, 47, 25),
    _pos('primera_2', 'Primera (cen)', 'primera', 370, 300, 47, 25),
    _pos('primera_3', 'Primera (dre)', 'primera', 420, 300, 47, 25),
    _pos('vent_1', 'Vent esq', 'vent', 200, 120, 60, 25, -35),
    _pos('vent_2', 'Vent dre', 'vent', 520, 120, 60, 25, 35),
    _pos('vent_3', 'Vent esq2', 'vent', 200, 200, 60, 25, -35),
    _pos('vent_4', 'Vent dre2', 'vent', 520, 200, 60, 25, 35),
    _pos('lateral_1', 'Lateral esq', 'lateral', 200, 260, 55, 25, -15),
    _pos('lateral_2', 'Lateral dre', 'lateral', 530, 260, 55, 25, 15),
    _pos('crossa_1', 'Crossa esq', 'crossa', 290, 300, 40, 25),
    _pos('crossa_2', 'Crossa dre', 'crossa', 450, 300, 40, 25),
    _pos('contrafort_1', 'Contrafort esq', 'contrafort', 310, 340, 40, 25),
    _pos('contrafort_2', 'Contrafort cen', 'contrafort', 370, 340, 40, 25),
    _pos('contrafort_3', 'Contrafort dre', 'contrafort', 430, 340, 40, 25),
    _pos('agulla_1', 'Agulla esq', 'agulla', 250, 150, 40, 25),
    _pos('agulla_2', 'Agulla dre', 'agulla', 490, 150, 40, 25),
]

T4D6_POS = [
    _pos('enxaneta', 'Enxaneta', 'enxaneta', 370, 30, 60, 25),
    _pos('acotxador', 'Acotxador', 'acotxador', 370, 60, 60, 25),
    _pos('dos_1', 'Dos (esq)', 'dos', 340, 90, 55, 25),
    _pos('dos_2', 'Dos (dre)', 'dos', 400, 90, 55, 25),
    _pos('quint_1', 'Quint 1', 'quint', 295, 120, 43, 25),
    _pos('quint_2', 'Quint 2', 'quint', 345, 120, 43, 25),
    _pos('quint_3', 'Quint 3', 'quint', 395, 120, 43, 25),
    _pos('quint_4', 'Quint 4', 'quint', 445, 120, 43, 25),
    _pos('quart_1', 'Quart 1', 'quart', 295, 150, 43, 25),
    _pos('quart_2', 'Quart 2', 'quart', 345, 150, 43, 25),
    _pos('quart_3', 'Quart 3', 'quart', 395, 150, 43, 25),
    _pos('quart_4', 'Quart 4', 'quart', 445, 150, 43, 25),
    _pos('terç_1', 'Terç 1', 'terç', 295, 180, 43, 25),
    _pos('terç_2', 'Terç 2', 'terç', 345, 180, 43, 25),
    _pos('terç_3', 'Terç 3', 'terç', 395, 180, 43, 25),
    _pos('terç_4', 'Terç 4', 'terç', 445, 180, 43, 25),
    _pos('segon_1', 'Segon 1', 'segon', 295, 210, 43, 25),
    _pos('segon_2', 'Segon 2', 'segon', 345, 210, 43, 25),
    _pos('segon_3', 'Segon 3', 'segon', 395, 210, 43, 25),
    _pos('segon_4', 'Segon 4', 'segon', 445, 210, 43, 25),
    _pos('baix_1', 'Baix 1', 'baix', 295, 240, 43, 25),
    _pos('baix_2', 'Baix 2', 'baix', 345, 240, 43, 25),
    _pos('baix_3', 'Baix 3', 'baix', 395, 240, 43, 25),
    _pos('baix_4', 'Baix 4', 'baix', 445, 240, 43, 25),
    _pos('primera_1', 'Primera 1', 'primera', 315, 290, 40, 25),
    _pos('primera_2', 'Primera 2', 'primera', 370, 290, 40, 25),
    _pos('primera_3', 'Primera 3', 'primera', 425, 290, 40, 25),
    _pos('vent_1', 'Vent esq', 'vent', 180, 110, 55, 25, -35),
    _pos('vent_2', 'Vent dre', 'vent', 545, 110, 55, 25, 35),
    _pos('vent_3', 'Vent esq2', 'vent', 180, 190, 55, 25, -35),
    _pos('vent_4', 'Vent dre2', 'vent', 545, 190, 55, 25, 35),
    _pos('lateral_1', 'Lateral esq', 'lateral', 190, 250, 50, 25, -15),
    _pos('lateral_2', 'Lateral dre', 'lateral', 540, 250, 50, 25, 15),
    _pos('crossa_1', 'Crossa esq', 'crossa', 280, 290, 30, 25),
    _pos('crossa_2', 'Crossa dre', 'crossa', 470, 290, 30, 25),
    _pos('contrafort_1', 'Contrafort 1', 'contrafort', 305, 330, 30, 25),
    _pos('contrafort_2', 'Contrafort 2', 'contrafort', 345, 330, 30, 25),
    _pos('contrafort_3', 'Contrafort 3', 'contrafort', 385, 330, 30, 25),
    _pos('contrafort_4', 'Contrafort 4', 'contrafort', 425, 330, 30, 25),
    _pos('agulla_1', 'Agulla esq', 'agulla', 240, 140, 35, 25),
    _pos('agulla_2', 'Agulla dre', 'agulla', 510, 140, 35, 25),
]


TEMPLATES = [
    {'name': 'p4', 'display_name': 'Pilar de 4', 'positions': P4_POS},
    {'name': 'p5', 'display_name': 'Pilar de 5', 'positions': P5_POS},
    {'name': '2d6', 'display_name': '2 de 6', 'positions': T2D6_POS},
    {'name': '2d6n', 'display_name': '2 de 6 net', 'positions': T2D6N_POS},
    {'name': '3d6', 'display_name': '3 de 6', 'positions': T3D6_POS},
    {'name': '4d6', 'display_name': '4 de 6', 'positions': T4D6_POS},
]


def _seed_templates():
    if CastellTemplate.query.first():
        return

    for t in TEMPLATES:
        template = CastellTemplate(name=t['name'], display_name=t['display_name'])
        db.session.add(template)
        db.session.flush()
        for pos in t['positions']:
            name, label, role, x, y, w, h, angle, color, text_color = pos
            db.session.add(CastellPosition(
                template_id=template.id,
                name=name, label=label, role=role,
                x=x, y=y, w=w, h=h, angle=angle,
                color=color, text_color=text_color,
            ))
    db.session.commit()


def _seed_test_event():
    if Event.query.filter_by(title='Assaig de proves').first():
        return

    test_event = Event(
        title='Assaig de proves',
        date=datetime(2026, 7, 10, 20, 0),
        type='assaig',
        description='Assaig de proves per provar l\'aplicació Pinyator.',
    )
    db.session.add(test_event)
    db.session.flush()

    castellers = User.query.filter_by(role='casteller').all()
    random.shuffle(castellers)
    going = castellers[:50]

    for user in going:
        db.session.add(Attendance(user_id=user.id, event_id=test_event.id, status='va'))

    for user in castellers[50:75]:
        db.session.add(Attendance(user_id=user.id, event_id=test_event.id, status='no_va'))

    for user in castellers[75:]:
        db.session.add(Attendance(user_id=user.id, event_id=test_event.id, status='no_ho_sap'))

    db.session.commit()

    template = CastellTemplate.query.first()
    if template:
        ec = EventCastell(
            event_id=test_event.id,
            template_id=template.id,
            name=f'{template.display_name} de prova',
        )
        db.session.add(ec)
        db.session.commit()
