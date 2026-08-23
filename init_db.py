"""
init_db.py — Seed database dengan data PPDS PA UNAIR yang realistis.
Jalankan: python init_db.py
"""
from app import app
from models import db, User, CompetencyLog, Exam, AcademicTask, ExternalRotation, Reminder
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def assign_standard_curriculum(user_id, is_seed=False):
    # ── Competency Logs ───────────────────────────────────────────────────
    competencies = [
        # Tahap Merah
        ('red', 'Metodologi Penelitian & Statistik', 'Dasar & Metodologi'),
        ('red', 'Imunologi Dasar', 'Dasar & Metodologi'),
        ('red', 'Epidemiologi Klinik', 'Dasar & Metodologi'),
        ('red', 'Farmakologi Klinik', 'Dasar & Metodologi'),
        ('red', 'Dasar Pertolongan Darurat', 'Dasar & Metodologi'),
        ('red', 'Biologi Molekuler', 'Dasar & Metodologi'),
        ('red', 'Filsafat Ilmu', 'Dasar & Metodologi'),
        ('red', 'Etika Hukum Kedokteran & Hubungan Antar Manusia', 'Dasar & Metodologi'),
        ('red', 'Metode Belajar Mengajar', 'Dasar & Metodologi'),
        ('red', 'Penulisan Karya Ilmiah', 'Dasar & Metodologi'),
        ('red', 'Teknik Laboratorium Histologi & Histokimia', 'Laboratorium Dasar'),
        ('red', 'Patologi Kepala & Leher', 'Sistem Organ'),
        ('red', 'Sitologi Aspiratif II', 'Sitologi'),
        ('red', 'Patologi Kulit', 'Sistem Organ'),
        ('red', 'Patologi Mediastinum & Kardiovaskuler', 'Sistem Organ'),
        ('red', 'Patologi Sistem Saraf & Mata', 'Sistem Organ'),
        ('red', 'Patologi Muskuloskeletal II', 'Sistem Organ'),
        ('red', 'Patologi Integrated II', 'Integrated'),
        ('red', 'Otopsi Klinik', 'Diagnostik Khusus'),
        ('red', 'Diagnostik Histopatologi', 'Diagnostik Khusus'),
        ('red', 'Diagnostik FNAB', 'Diagnostik Khusus'),

        # Tahap Kuning
        ('yellow', 'Teknik Sitologi & Teknik Potong Beku', 'Teknik Khusus'),
        ('yellow', 'Dasar Imunohistokimia & Patologi Molekuler', 'Patologi Molekuler'),
        ('yellow', 'Dasar Penelitian Bidang Patologi & Patologi Eksperimental', 'Metodologi'),
        ('yellow', 'Patologi Umum', 'Dasar Patologi'),
        ('yellow', 'Etika Dokter Spesialis Patologi', 'Etika & Profesi'),
        ('yellow', 'Dasar Patologi Organ', 'Sistem Organ'),
        ('yellow', 'Proposal Karya Akhir (Target Mandatori)', 'Akademik & Penelitian'),
        ('yellow', 'Diagnostik Imunohistokimia', 'Diagnostik Khusus'),

        # Tahap Hijau
        ('green', 'Patologi Genetalia Wanita I & II', 'Sistem Organ'),
        ('green', 'Patologi Payudara', 'Sistem Organ'),
        ('green', 'Patologi Sistem Respirasi', 'Sistem Organ'),
        ('green', 'Patologi Ginjal', 'Sistem Organ'),
        ('green', 'Patologi Saluran Cerna', 'Sistem Organ'),
        ('green', 'Patologi Endokrin', 'Sistem Organ'),
        ('green', 'Patologi Hepatobilier & Pankreas', 'Sistem Organ'),
        ('green', 'Patologi Saluran Kemih & Genitalia Pria', 'Sistem Organ'),
        ('green', 'Patologi Hematolimfoid', 'Sistem Organ'),
        ('green', 'Patologi Muskuloskeletal I', 'Sistem Organ'),
        ('green', 'Sitologi Exfoliatif', 'Sitologi'),
        ('green', 'Sitologi Aspiratif I', 'Sitologi'),
        ('green', 'Patologi Integrated I, II & III', 'Integrated'),
        ('green', 'Diagnostik Potong Beku', 'Diagnostik Khusus'),
        ('green', 'Pengelolaan Laboratorium PA', 'Manajemen'),
        ('green', 'Diagnostik PA Luar', 'Stase Luar'),
        ('green', 'Pendidikan Patologi Anatomi', 'Edukasi'),
        ('green', 'Karya Akhir & Publikasi Scopus', 'Akademik & Penelitian'),
    ]
    for phase, name, organ in competencies:
        status = 'not_started'
        if is_seed:
            if name in ('Imunologi Dasar', 'Biologi Molekuler & Genetika'):
                status = 'completed'
            elif name == 'Patologi Kepala & Leher':
                status = 'in_progress'

        db.session.add(CompetencyLog(
            user_id=user_id,
            phase_category=phase,
            competency_name=name,
            organ_system=organ,
            status=status,
            completed_at=datetime.utcnow() if status == 'completed' else None,
        ))

    # ── Exams ─────────────────────────────────────────────────────────────
    exams = [
        ('Ujian Lokal Tahap 1', 'Lokal Tahap 1', 'Syarat naik Kalung Kuning'),
        ('Ujian Nasional Tahap 1', 'Nasional Tahap 1', 'Syarat: Wajib Lulus Ujian Lokal Tahap 1'),
        ('Ujian Lokal Tahap 2', 'Lokal Tahap 2', 'Diikuti di akhir masa Kalung Hijau'),
        ('Ujian Board / Nasional Tahap 2', 'Board/Tahap 2', 'Syarat: Lulus Ujian Lokal Tahap 2 & Punya LOA Publikasi Scopus'),
    ]
    for name, etype, notes in exams:
        result, score, sdate = 'terjadwal', None, None
        if is_seed:
            if name == 'Ujian Lokal Tahap 1':
                result, score, sdate = 'lulus', 82.5, datetime(2025, 3, 15)
            elif name == 'Ujian Nasional Tahap 1':
                result, score, sdate = 'lulus', 78.0, datetime(2025, 6, 20)

        db.session.add(Exam(
            user_id=user_id,
            exam_name=name,
            exam_type=etype,
            scheduled_date=sdate,
            result=result,
            score=score,
            notes=notes,
        ))

    # ── Academic Tasks ────────────────────────────────────────────────────
    now = datetime.utcnow()
    tasks = [
        # Semester 1
        ('Textbook Reading', 'Textbook Reading 1', 'Wajib 1 Textbook Reading di Semester 1', 1),
        ('Journal Reading', 'Journal Reading 1', 'Wajib 1 Journal Reading di Semester 1', 1),
        ('Tugas Ilmiah', 'Case Report 1', 'Penyusunan laporan kasus', 1),
        ('Tugas Ilmiah', 'Case Report 2', 'Penyusunan laporan kasus', 1),
        ('Tugas Ilmiah', 'Tinjauan Pustaka / Referat', 'Penyusunan tinjauan pustaka', 1),
        ('Penelitian', 'Telaah Retrospektif', 'Harus memiliki ethical clearance jika menggunakan data klinis', 1),
        ('Journal Reading', 'Journal Reading Tambahan', 'Review jurnal ilmiah tambahan', 1),

        # Semester 4
        ('Penelitian', 'Proposal Karya Akhir', 'Sering bergeser ke semester 5/6', 4),
        ('Etik', 'Pengajuan Persetujuan Etik (Ethical Clearance)', 'Wajib diajukan setelah proposal disetujui, sebelum ambil data', 4),

        # Semester 7
        ('Penelitian', 'Karya Akhir Selesai', 'Wajib disubmit ke jurnal terakreditasi', 7),
        ('Publikasi', 'Dapatkan LOA Publikasi', 'Syarat mutlak mendaftar Ujian Nasional Tahap 2', 7),

        # Semester 8
        ('Publikasi', 'Publikasi Jurnal Terindeks Scopus', 'Syarat Mutlak Kelulusan Universitas', 8),
        ('Etik', 'Laporan Penutupan Etik (Tutup Etik)', 'Wajib dilakukan ke komite etik setelah naskah dipublikasikan', 8),
    ]
    for ttype, title, desc, sem in tasks:
        done = False
        dl = None
        if is_seed:
            if sem == 1:
                done = True
            elif sem == 4:
                dl = now + timedelta(days=60)
                if 'Proposal' in title:
                    dl = now + timedelta(days=90)

        db.session.add(AcademicTask(
            user_id=user_id,
            task_type=ttype,
            title=title,
            description=desc,
            target_semester=sem,
            deadline=dl,
            is_completed=done,
        ))

    # ── External Rotations ────────────────────────────────────────────────
    rotations = [
        ('RS Universitas Airlangga (RSUA)', 'Departemen Patologi Anatomi', 'Surabaya', 'Prof. Dr. Soemarsono, Sp.PA(K)'),
        ('RSUD Dr. Soetomo', 'Patologi Anatomi', 'Surabaya', 'Dr. Ratna Kusuma, Sp.PA'),
        ('RSPAL Dr. Ramelan', 'Lab Patologi', 'Surabaya', 'Dr. Adi Purnomo, Sp.PA'),
        ('RSUD Haji Surabaya', 'Patologi Anatomi', 'Surabaya', None),
    ]
    for hname, dept, city, sup in rotations:
        status = 'terjadwal'
        sdate, edate = None, None
        if is_seed:
            if hname == 'RS Universitas Airlangga (RSUA)':
                status, sdate, edate = 'selesai', datetime(2025, 1, 6), datetime(2025, 3, 31)
            elif hname == 'RSUD Dr. Soetomo':
                status, sdate, edate = 'selesai', datetime(2025, 7, 1), datetime(2025, 9, 30)
            elif hname == 'RSPAL Dr. Ramelan':
                status, sdate, edate = 'aktif', datetime(2026, 1, 6), datetime(2026, 3, 31)
            elif hname == 'RSUD Haji Surabaya':
                sdate, edate = datetime(2026, 7, 1), datetime(2026, 9, 30)

        db.session.add(ExternalRotation(
            user_id=user_id,
            hospital_name=hname,
            department=dept,
            city=city,
            supervisor=sup,
            start_date=sdate,
            end_date=edate,
            status=status,
        ))


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

        assign_standard_curriculum(u.id, is_seed=True)

        db.session.commit()
        print('✅ Database berhasil di-seed!')
        print('   Login: ppds@unair.ac.id / password')


if __name__ == '__main__':
    seed()
