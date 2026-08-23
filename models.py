from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    nim = db.Column(db.String(50), nullable=True)
    current_semester = db.Column(db.Integer, default=1)
    phase = db.Column(db.String(16), default='MKDU')  # MKDU, red, yellow, green
    role = db.Column(db.String(16), default='ppds')   # ppds, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reminders = db.relationship('Reminder', backref='user', lazy=True)
    competency_logs = db.relationship('CompetencyLog', backref='user', lazy=True)
    exams = db.relationship('Exam', backref='user', lazy=True)
    academic_tasks = db.relationship('AcademicTask', backref='user', lazy=True)
    external_rotations = db.relationship('ExternalRotation', backref='user', lazy=True)


class CompetencyLog(db.Model):
    __tablename__ = 'competency_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phase_category = db.Column(db.String(16), nullable=False)  # red, yellow, green
    competency_name = db.Column(db.String(200), nullable=False)
    organ_system = db.Column(db.String(100), nullable=True)    # e.g. Kepala & Leher, Mammae
    status = db.Column(db.String(32), default='not_started')   # not_started, pending_verification, completed
    evidence_url = db.Column(db.String(500), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Exam(db.Model):
    __tablename__ = 'exam'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_name = db.Column(db.String(200), nullable=False)      # e.g. "Ujian Lokal Organ Kepala & Leher"
    exam_type = db.Column(db.String(100), nullable=False)      # Lokal, Nasional Tahap 1, Board/Tahap 2
    scheduled_date = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.String(32), default='terjadwal')     # terjadwal, lulus, tidak_lulus
    score = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AcademicTask(db.Model):
    __tablename__ = 'academic_task'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_type = db.Column(db.String(100), nullable=False)      # Textbook Reading, Journal Reading, Penelitian, Publikasi
    title = db.Column(db.String(300), nullable=False)          # judul buku/jurnal/karya akhir
    description = db.Column(db.Text, nullable=True)
    target_semester = db.Column(db.Integer, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    document_proof_url = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExternalRotation(db.Model):
    __tablename__ = 'external_rotation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hospital_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    supervisor = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(32), default='terjadwal')     # terjadwal, aktif, selesai
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reminder(db.Model):
    __tablename__ = 'reminder'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    time = db.Column(db.String(64))
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
