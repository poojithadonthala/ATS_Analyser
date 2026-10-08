from datetime import datetime
from sqlalchemy import create_engine, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column, Mapped, relationship
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_URL = 'sqlite:///' + str(ROOT / 'hirex.db')
engine = create_engine(DB_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
class Base(DeclarativeBase): pass

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()

class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[str]=mapped_column(String(20), default='student')
    department: Mapped[str]=mapped_column(String(120), nullable=True)
    register_number: Mapped[str]=mapped_column(String(80), nullable=True)
    profile_photo: Mapped[str]=mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)

def migrate_schema():
    """Add backward-compatible profile fields to existing local SQLite installs."""
    with engine.begin() as conn:
        columns={row[1] for row in conn.exec_driver_sql('PRAGMA table_info(users)').fetchall()}
        for name,sql_type in [('department','VARCHAR(120)'),('register_number','VARCHAR(80)'),('profile_photo','VARCHAR(500)')]:
            if name not in columns:
                conn.exec_driver_sql(f'ALTER TABLE users ADD COLUMN {name} {sql_type}')
        conn.exec_driver_sql("CREATE UNIQUE INDEX IF NOT EXISTS uq_student_register_number ON users(register_number) WHERE role = 'student' AND register_number IS NOT NULL")
        conn.exec_driver_sql("CREATE UNIQUE INDEX IF NOT EXISTS uq_student_register_number_ci ON users(lower(register_number)) WHERE role = 'student' AND register_number IS NOT NULL")
        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_users_department ON users(department)")
        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_jobs_title ON jobs(title)")

class Job(Base):
    __tablename__='jobs'
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(160))
    description: Mapped[str]=mapped_column(Text)
    minimum_score: Mapped[int]=mapped_column(Integer, default=70)
    required_skills: Mapped[str]=mapped_column(Text)
    optional_skills: Mapped[str]=mapped_column(Text, default='')
    active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_by: Mapped[int]=mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__='applications'
    id: Mapped[int]=mapped_column(primary_key=True)
    student_id: Mapped[int]=mapped_column(ForeignKey('users.id'), index=True)
    job_id: Mapped[int]=mapped_column(ForeignKey('jobs.id'), index=True)
    status: Mapped[str]=mapped_column(String(40), default='Applied')
    current_stage: Mapped[str]=mapped_column(String(40), default='ATS Screening')
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    student: Mapped['User']=relationship(foreign_keys=[student_id])
    job: Mapped['Job']=relationship(foreign_keys=[job_id])
    resume: Mapped['Resume']=relationship(back_populates='application', uselist=False)
    result: Mapped['ATSResult']=relationship(back_populates='application', uselist=False)

class Resume(Base):
    __tablename__='resumes'
    id: Mapped[int]=mapped_column(primary_key=True)
    student_id: Mapped[int]=mapped_column(ForeignKey('users.id'))
    application_id: Mapped[int]=mapped_column(ForeignKey('applications.id'), unique=True)
    filename: Mapped[str]=mapped_column(String(255))
    file_path: Mapped[str]=mapped_column(String(500))
    extracted_text: Mapped[str]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    application: Mapped[Application]=relationship(back_populates='resume')

class ATSResult(Base):
    __tablename__='ats_results'
    id: Mapped[int]=mapped_column(primary_key=True)
    application_id: Mapped[int]=mapped_column(ForeignKey('applications.id'), unique=True)
    overall_score: Mapped[float]=mapped_column(Float)
    details: Mapped[str]=mapped_column(Text)
    qualification_status: Mapped[str]=mapped_column(String(30))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    application: Mapped[Application]=relationship(back_populates='result')

