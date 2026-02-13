from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, JSON, ForeignKey, func, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    college_name = Column(String(255))
    roll_no = Column(String(100))
    branch = Column(String(100))
    year_of_study = Column(Integer)
    github_url = Column(String(255))
    linkedin_url = Column(String(255))
    profile_picture_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    mcq_attempts = relationship("MCQAttempt", back_populates="user", cascade="all, delete-orphan")
    programming_attempts = relationship("ProgrammingQuestionAttempt", back_populates="user", cascade="all, delete-orphan")
    stage1_result = relationship("Stage1Result", back_populates="user", uselist=False, cascade="all, delete-orphan")
    stage2_project = relationship("Stage2Project", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")


class MCQQuestion(Base):
    __tablename__ = 'mcq_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(CHAR(1), nullable=False)
    difficulty_level = Column(String(20))
    topic = Column(String(100))
    marks = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    attempts = relationship("MCQAttempt", back_populates="question", cascade="all, delete-orphan")


class ProgrammingProblem(Base):
    __tablename__ = 'programming_problems'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty_level = Column(String(20))
    time_limit = Column(Integer)
    memory_limit = Column(Integer)
    marks = Column(Integer, default=10)
    input_format = Column(Text)
    output_format = Column(Text)
    constraints = Column(Text)
    sample_input = Column(Text)
    sample_output = Column(Text)
    starter_code_python = Column(Text)
    starter_code_java = Column(Text)
    starter_code_cpp = Column(Text)
    starter_code_javascript = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    attempts = relationship("ProgrammingQuestionAttempt", back_populates="problem", cascade="all, delete-orphan")


class MCQAttempt(Base):
    __tablename__ = 'mcq_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('mcq_questions.id', ondelete='CASCADE'), nullable=False)
    selected_option = Column(CHAR(1))
    is_correct = Column(Boolean)
    attempted_at = Column(TIMESTAMP, server_default=func.now())
    time_taken = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="mcq_attempts")
    question = relationship("MCQQuestion", back_populates="attempts")


class ProgrammingQuestionAttempt(Base):
    __tablename__ = 'programming_question_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    problem_id = Column(Integer, ForeignKey('programming_problems.id', ondelete='CASCADE'), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(String(50))
    tab_inactivity_count = Column(Integer, default=0)
    score = Column(DECIMAL(5, 2), default=0)
    ai_feedback = Column(Text)
    submitted_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="programming_attempts")
    problem = relationship("ProgrammingProblem", back_populates="attempts")


class Stage1Result(Base):
    __tablename__ = 'stage1_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    mcq_score = Column(DECIMAL(5, 2), default=0)
    programming_score = Column(DECIMAL(5, 2), default=0)
    total_score = Column(DECIMAL(5, 2), default=0)
    rank = Column(Integer)
    is_qualified = Column(Boolean, default=False)
    completed_at = Column(TIMESTAMP)
    time_taken = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="stage1_result")


class Stage2Project(Base):
    __tablename__ = 'stage2_projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    project_title = Column(String(255))
    project_description = Column(Text)
    github_repo_url = Column(String(255))
    live_demo_url = Column(String(255))
    tech_stack = Column(JSON)
    screenshots = Column(JSON)
    submission_status = Column(String(50), default='not_started')
    submitted_at = Column(TIMESTAMP)
    ui_ux_score = Column(DECIMAL(5, 2))
    functionality_score = Column(DECIMAL(5, 2))
    code_quality_score = Column(DECIMAL(5, 2))
    innovation_score = Column(DECIMAL(5, 2))
    total_score = Column(DECIMAL(5, 2))
    evaluator_comments = Column(Text)
    is_qualified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="stage2_project")


class ActivityLog(Base):
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")


class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50))
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
