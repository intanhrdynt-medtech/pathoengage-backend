"""
init_db.py — Seed database dengan data PPDS PA UNAIR yang realistis.
Jalankan: python init_db.py
"""
from app import app
from models import db, User, CompetencyLog, Exam, AcademicTask, ExternalRotation, Reminder
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def seed():
    with app.app_context():
        # Reset schema
        db.drop_all()
        db.create_all()

        # ── Sample PPDS user ──────────────────────────────────────────────────
        u = User(
            email='ppds@unair.ac.id',
            password_hash=generate_password_hash('password'),
            full_name='Dr. Budi Santoso',
            nim='012345678',
            current_semester=4,
            phase='yellow',
            role='ppds',
        )
        db.session.add(u)
        db.session.flush()  # get u.id

        # ── Competency Logs ───────────────────────────────────────────────────
        competencies = [
            # (phase_category, competency_name, organ_system, status)
            ('red', 'Imunologi Dasar', 'Dasar PA', 'completed'),
            ('red', 'Biologi Molekuler & Genetika', 'Dasar PA', 'completed'),
            ('red', 'Patologi Kepala & Leher', 'Kepala & Leher', 'in_progress'),
            ('red', 'Patologi Paru', 'Paru', 'not_started'),
            ('yellow', 'Teknik Sitologi & Potong Beku', 'Sitologi', 'not_started'),
            ('yellow', 'Dasar Imunohistokimia (IHK)', 'IHK & Mol. Patologi', 'not_started'),
            ('yellow', 'Patologi Molekuler Dasar', 'IHK & Mol. Patologi', 'not_started'),
            ('yellow', 'Patologi Gastrointestinal', 'GIT', 'not_started'),
            ('green', 'Patologi Payudara', 'Payudara', 'not_started'),
            ('green', 'Patologi Ginjal & Urologi', 'Urologi', 'not_started'),
            ('green', 'Patologi Sistem Saraf Pusat', 'Neuropatologi', 'not_started'),
            ('green', 'Forensik Patologi', 'Forensik', 'not_started'),
        ]
        for phase, name, organ, status in competencies:
            db.session.add(CompetencyLog(
                user_id=u.id,
                phase_category=phase,
                competency_name=name,
                organ_system=organ,
                status=status,
                completed_at=datetime.utcnow() if status == 'completed' else None,
            ))

        # ── Exams ─────────────────────────────────────────────────────────────
        # Sesuai requirement: Ujian Lokal (organ) + Nasional Tahap 1 + Board/Tahap 2
        exams = [
            # (exam_name, exam_type, scheduled_date, result, score)
            ('Ujian Organ Kepala & Leher', 'Lokal', datetime(2025, 3, 15), 'lulus', 82.5),
            ('Ujian Organ Paru', 'Lokal', datetime(2025, 6, 20), 'lulus', 78.0),
            ('Ujian Organ GIT', 'Lokal', datetime(2026, 9, 10), 'terjadwal', None),
            ('Ujian Nasional Tahap 1', 'Nasional Tahap 1', datetime(2027, 3, 1), 'terjadwal', None),
            ('Ujian Board / Sp.PA', 'Board/Tahap 2', datetime(2028, 6, 1), 'terjadwal', None),
        ]
        for name, etype, sdate, result, score in exams:
            db.session.add(Exam(
                user_id=u.id,
                exam_name=name,
                exam_type=etype,
                scheduled_date=sdate,
                result=result,
                score=score,
            ))

        # ── Academic Tasks ────────────────────────────────────────────────────
        # Sesuai requirement: Textbook/Journal Reading (per semester), Proposal, Publikasi Scopus
        now = datetime.utcnow()
        tasks = [
            # (task_type, title, description, target_semester, deadline, is_completed)
            ('Textbook Reading', 'Robbins & Cotran Pathologic Basis of Disease',
             'Baca minimal 3 bab per bulan', 1, None, True),
            ('Textbook Reading', 'Rosai and Ackerman\'s Surgical Pathology',
             'Fokus pada bab organ yang sedang distase', 2, None, True),
            ('Journal Reading', 'Modern Pathology — Breast Carcinoma Update',
             'Presentasikan di journal reading department', 3, now + timedelta(days=30), False),
            ('Journal Reading', 'American Journal of Surgical Pathology',
             'Review jurnal terbaru IHK', 4, now + timedelta(days=60), False),
            ('Penelitian', 'Proposal Karya Akhir (KA)',
             'Penelitian tentang Imunohistokimia pada Kanker Payudara Triple Negative', 4,
             now + timedelta(days=90), False),
            ('Publikasi', 'Publikasi Jurnal Terindeks Scopus',
             'Syarat kelulusan: minimal 1 artikel terindeks Scopus atau setara', 8, None, False),
        ]
        for ttype, title, desc, sem, dl, done in tasks:
            db.session.add(AcademicTask(
                user_id=u.id,
                task_type=ttype,
                title=title,
                description=desc,
                target_semester=sem,
                deadline=dl,
                is_completed=done,
            ))

        # ── External Rotations ────────────────────────────────────────────────
        # Stase luar sesuai requirement
        rotations = [
            # (hospital_name, department, city, supervisor, start, end, status)
            ('RS Universitas Airlangga (RSUA)', 'Departemen Patologi Anatomi', 'Surabaya',
             'Prof. Dr. Soemarsono, Sp.PA(K)',
             datetime(2025, 1, 6), datetime(2025, 3, 31), 'selesai'),
            ('RSUD Dr. Soetomo', 'Patologi Anatomi', 'Surabaya',
             'Dr. Ratna Kusuma, Sp.PA',
             datetime(2025, 7, 1), datetime(2025, 9, 30), 'selesai'),
            ('RSPAL Dr. Ramelan', 'Lab Patologi', 'Surabaya',
             'Dr. Adi Purnomo, Sp.PA',
             datetime(2026, 1, 6), datetime(2026, 3, 31), 'aktif'),
            ('RSUD Haji Surabaya', 'Patologi Anatomi', 'Surabaya',
             None, datetime(2026, 7, 1), datetime(2026, 9, 30), 'terjadwal'),
        ]
        for hname, dept, city, sup, sdate, edate, status in rotations:
            db.session.add(ExternalRotation(
                user_id=u.id,
                hospital_name=hname,
                department=dept,
                city=city,
                supervisor=sup,
                start_date=sdate,
                end_date=edate,
                status=status,
            ))

        db.session.commit()
        print('✅ Database berhasil di-seed!')
        print('   Login: ppds@unair.ac.id / password')


if __name__ == '__main__':
    seed()
