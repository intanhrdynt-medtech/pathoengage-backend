import os
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Reminder, CompetencyLog, Exam, AcademicTask, ExternalRotation

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-ppds-pa-unair')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./backend_data.db')

app = Flask(__name__)
CORS(app)  # Allows Flutter to reach Flask

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)


# ── Helpers ──────────────────────────────────────────────────────────────────

def encode_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except Exception:
        return None


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Missing token'}), 401
        token = auth.split(' ', 1)[1]
        user_id = decode_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        request.user = user
        return f(*args, **kwargs)
    return decorated


def user_dict(user):
    return {
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'nim': user.nim,
        'phase': user.phase,
        'current_semester': user.current_semester,
        'role': user.role,
    }


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'PathoEngage API is running on Vercel!'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'app': 'PathoEngage PPDS PA UNAIR'})

@app.route('/seed')
def run_seed():
    import init_db
    try:
        init_db.seed()
        return jsonify({'status': 'success', 'message': 'Database seeded successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    nim = data.get('nim', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email dan password wajib diisi'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password minimal 6 karakter'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email sudah terdaftar'}), 400

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        full_name=full_name or email,
        nim=nim or '-',
    )
    db.session.add(user)
    db.session.flush() # get user.id before assigning curriculum
    
    # Assign standard curriculum to the new user
    import init_db
    init_db.assign_standard_curriculum(user.id, is_seed=False)
    
    db.session.commit()
    token = encode_token(user.id)
    return jsonify({'token': token, 'user': user_dict(user)})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email dan password wajib diisi'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Email atau password salah'}), 401

    token = encode_token(user.id)
    return jsonify({'token': token, 'user': user_dict(user)})


@app.route('/me', methods=['GET'])
@auth_required
def me():
    return jsonify(user_dict(request.user))


# ── Competencies ──────────────────────────────────────────────────────────────

def comp_dict(c):
    return {
        'id': c.id,
        'phase_category': c.phase_category,
        'competency_name': c.competency_name,
        'organ_system': c.organ_system,
        'status': c.status,
        'evidence_url': c.evidence_url,
        'notes': c.notes,
        'completed_at': c.completed_at.isoformat() if c.completed_at else None,
    }


@app.route('/competencies', methods=['GET'])
@auth_required
def get_competencies():
    return jsonify([comp_dict(c) for c in request.user.competency_logs])


@app.route('/competencies/<int:cid>', methods=['PUT'])
@auth_required
def update_competency(cid):
    comp = CompetencyLog.query.filter_by(id=cid, user_id=request.user.id).first()
    if not comp:
        return jsonify({'error': 'Tidak ditemukan'}), 404
    data = request.get_json() or {}
    if 'status' in data:
        comp.status = data['status']
        comp.completed_at = datetime.datetime.utcnow() if comp.status == 'completed' else None
    if 'evidence_url' in data:
        comp.evidence_url = data['evidence_url']
    if 'notes' in data:
        comp.notes = data['notes']
    db.session.commit()
    return jsonify(comp_dict(comp))


# ── Exams ─────────────────────────────────────────────────────────────────────

def exam_dict(e):
    return {
        'id': e.id,
        'exam_name': e.exam_name,
        'exam_type': e.exam_type,
        'scheduled_date': e.scheduled_date.isoformat() if e.scheduled_date else None,
        'result': e.result,
        'score': e.score,
        'notes': e.notes,
    }


@app.route('/exams', methods=['GET'])
@auth_required
def get_exams():
    return jsonify([exam_dict(e) for e in request.user.exams])


@app.route('/exams/<int:eid>', methods=['PUT'])
@auth_required
def update_exam(eid):
    exam = Exam.query.filter_by(id=eid, user_id=request.user.id).first()
    if not exam:
        return jsonify({'error': 'Tidak ditemukan'}), 404
    data = request.get_json() or {}
    for field in ['result', 'score', 'notes', 'scheduled_date']:
        if field in data:
            setattr(exam, field, data[field])
    db.session.commit()
    return jsonify(exam_dict(exam))


# ── Academic Tasks ────────────────────────────────────────────────────────────

def task_dict(t):
    return {
        'id': t.id,
        'task_type': t.task_type,
        'title': t.title,
        'description': t.description,
        'target_semester': t.target_semester,
        'deadline': t.deadline.isoformat() if t.deadline else None,
        'is_completed': t.is_completed,
        'document_proof_url': t.document_proof_url,
    }


@app.route('/academic-tasks', methods=['GET'])
@auth_required
def get_academic_tasks():
    return jsonify([task_dict(t) for t in request.user.academic_tasks])


@app.route('/academic-tasks/<int:tid>', methods=['PUT'])
@auth_required
def update_academic_task(tid):
    task = AcademicTask.query.filter_by(id=tid, user_id=request.user.id).first()
    if not task:
        return jsonify({'error': 'Tidak ditemukan'}), 404
    data = request.get_json() or {}
    for field in ['is_completed', 'document_proof_url', 'description']:
        if field in data:
            setattr(task, field, data[field])
    db.session.commit()
    return jsonify(task_dict(task))


# ── External Rotations ────────────────────────────────────────────────────────

def rotation_dict(r):
    return {
        'id': r.id,
        'hospital_name': r.hospital_name,
        'department': r.department,
        'city': r.city,
        'supervisor': r.supervisor,
        'start_date': r.start_date.isoformat() if r.start_date else None,
        'end_date': r.end_date.isoformat() if r.end_date else None,
        'status': r.status,
        'notes': r.notes,
    }


@app.route('/rotations', methods=['GET'])
@auth_required
def get_rotations():
    return jsonify([rotation_dict(r) for r in request.user.external_rotations])


@app.route('/rotations/<int:rid>', methods=['PUT'])
@auth_required
def update_rotation(rid):
    rot = ExternalRotation.query.filter_by(id=rid, user_id=request.user.id).first()
    if not rot:
        return jsonify({'error': 'Tidak ditemukan'}), 404
    data = request.get_json() or {}
    for field in ['status', 'notes', 'supervisor']:
        if field in data:
            setattr(rot, field, data[field])
    db.session.commit()
    return jsonify(rotation_dict(rot))


# ── Reminders ─────────────────────────────────────────────────────────────────

@app.route('/reminders', methods=['GET', 'POST'])
@auth_required
def handle_reminders():
    user = request.user
    if request.method == 'GET':
        return jsonify([{
            'id': r.id, 'title': r.title, 'description': r.description,
            'time': r.time, 'completed': r.completed
        } for r in user.reminders])
    data = request.get_json() or {}
    if not data.get('title'):
        return jsonify({'error': 'title required'}), 400
    reminder = Reminder(user_id=user.id, title=data['title'],
                        description=data.get('description'), time=data.get('time'))
    db.session.add(reminder)
    db.session.commit()
    return jsonify({'id': reminder.id, 'title': reminder.title}), 201


@app.route('/reminders/<int:rid>', methods=['PUT', 'DELETE'])
@auth_required
def update_reminder(rid):
    reminder = Reminder.query.filter_by(id=rid, user_id=request.user.id).first()
    if not reminder:
        return jsonify({'error': 'not found'}), 404
    if request.method == 'DELETE':
        db.session.delete(reminder)
        db.session.commit()
        return jsonify({'deleted': rid})
    data = request.get_json() or {}
    reminder.title = data.get('title', reminder.title)
    reminder.description = data.get('description', reminder.description)
    reminder.time = data.get('time', reminder.time)
    if 'completed' in data:
        reminder.completed = data['completed']
    db.session.commit()
    return jsonify({'id': reminder.id, 'title': reminder.title, 'completed': reminder.completed})


# ── User Phase Update ─────────────────────────────────────────────────────────

@app.route('/me/phase', methods=['PUT'])
@auth_required
def update_phase():
    data = request.get_json() or {}
    phase = data.get('phase')
    if phase not in ('MKDU', 'red', 'yellow', 'green'):
        return jsonify({'error': "phase harus salah satu dari: MKDU, red, yellow, green"}), 400
    request.user.phase = phase
    db.session.commit()
    return jsonify(user_dict(request.user))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
