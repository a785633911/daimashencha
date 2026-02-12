from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./mybrokencode.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class AIConfig(Base):
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    api_url = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    review_model = Column(String)
    recheck_model = Column(String)
    stream_enabled = Column(Boolean, default=False)
    reference_paths = Column(JSON)
    format_paths = Column(JSON)
    workflow_paths = Column(JSON)
    standard_paths = Column(JSON)
    is_active = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    sub_paths = Column(JSON)
    tags = Column(JSON)
    default_branch = Column(String)
    base_branch = Column(String)
    notes = Column(Text)
    icon = Column(String)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    branch = Column(String)
    file_path = Column(String)
    line_start = Column(Integer)
    line_end = Column(Integer)
    issue_type = Column(String)
    severity = Column(String)
    description = Column(Text)
    code_snippet = Column(Text)
    status = Column(String, default="待审核")
    is_ignored = Column(Boolean, default=False)
    ignore_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)

class ReviewRecord(Base):
    __tablename__ = "review_records"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    branch = Column(String)
    base_branch = Column(String)
    review_scope = Column(String)
    file_count = Column(Integer)
    issue_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProjectStats(Base):
    __tablename__ = "project_stats"

    project_id = Column(Integer, primary_key=True)
    total_reviews = Column(Integer, default=0)
    current_issues = Column(Integer, default=0)
    resolved_issues = Column(Integer, default=0)
    ignored_issues = Column(Integer, default=0)
    pending_issues = Column(Integer, default=0)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
