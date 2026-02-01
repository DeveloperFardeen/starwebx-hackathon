from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: str
    full_name: str

class UserProfileUpdate(BaseModel):
    phone: Optional[str] = None
    college_name: Optional[str] = None
    branch: Optional[str] = None
    year_of_study: Optional[int] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    college_name: Optional[str]
    branch: Optional[str]
    year_of_study: Optional[int]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    profile_picture_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth Schemas
class GoogleAuthRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# MCQ Schemas
class MCQQuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty_level: Optional[str]
    marks: int
    
    class Config:
        from_attributes = True

class MCQAnswerSubmit(BaseModel):
    question_id: int
    selected_option: str = Field(..., pattern="^[A-D]$")
    time_taken: Optional[int] = None


# Programming Problem Schemas
class ProgrammingProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty_level: Optional[str]
    marks: int
    input_format: Optional[str]
    output_format: Optional[str]
    constraints: Optional[str]
    sample_input: Optional[str]
    sample_output: Optional[str]
    starter_code_python: Optional[str]
    starter_code_java: Optional[str]
    starter_code_cpp: Optional[str]
    starter_code_javascript: Optional[str]
    
    class Config:
        from_attributes = True

class CodeSubmission(BaseModel):
    problem_id: int
    code: str
    language: str


# Stage 1 Results
class Stage1ResultResponse(BaseModel):
    user_id: int
    mcq_score: float
    programming_score: float
    total_score: float
    rank: Optional[int]
    is_qualified: bool
    
    class Config:
        from_attributes = True


# Stage 2 Project Schemas
class Stage2ProjectSubmit(BaseModel):
    project_title: str
    project_description: str
    github_repo_url: str
    live_demo_url: Optional[str] = None
    tech_stack: List[str]

class Stage2ProjectResponse(BaseModel):
    id: int
    user_id: int
    project_title: Optional[str]
    project_description: Optional[str]
    github_repo_url: Optional[str]
    live_demo_url: Optional[str]
    tech_stack: Optional[List]
    screenshots: Optional[List]
    submission_status: str
    submitted_at: Optional[datetime]
    total_score: Optional[float]
    is_qualified: bool
    
    class Config:
        from_attributes = True


# Notification Schema
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: Optional[str]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Response
class DashboardResponse(BaseModel):
    user: UserResponse
    stage1_status: Optional[str] = "not_started"  # not_started, in_progress, completed
    stage1_result: Optional[Stage1ResultResponse] = None
    stage2_status: Optional[str] = "locked"  # locked, available, submitted
    stage2_project: Optional[Stage2ProjectResponse] = None
    notifications_count: int = 0