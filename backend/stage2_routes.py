from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import json
import shutil
import uuid

from database import get_db
from models import User, Stage2Project, Stage1Result, Notification
from schemas import Stage2ProjectSubmit, Stage2ProjectResponse
from auth_routes import get_current_user, log_activity

router = APIRouter(prefix="/api/stage2", tags=["Stage 2"])

# Upload directory
# UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============== CHECK ELIGIBILITY ==============

def check_stage2_eligibility(user_id: int, db: Session):
    """Check if user is eligible for Stage 2"""
    stage1_result = db.query(Stage1Result).filter(
        Stage1Result.user_id == user_id,
        Stage1Result.is_qualified == True
    ).first()
    
    if not stage1_result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not qualified for Stage 2. Please complete and qualify Stage 1 first."
        )
    
    return stage1_result


# ============== PROJECT ASSIGNMENT ==============

@router.get("/assignment")
async def get_project_assignment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Stage 2 project assignment"""
    # Check eligibility
    check_stage2_eligibility(current_user.id, db)
    
    # Check if project already exists
    project = db.query(Stage2Project).filter(
        Stage2Project.user_id == current_user.id
    ).first()
    
    if not project:
        # Create new project assignment
        project = Stage2Project(
            user_id=current_user.id,
            submission_status='not_started'
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            title="Round 2 Unlocked! 🎉",
            message="You've qualified for Round 2! Build your mini-application and submit before Feb 13, 2026.",
            type="stage2_unlocked"
        )
        db.add(notification)
        db.commit()
    
    # Return assignment details
    assignment = {
        "title": "Build a Mini Application",
        "description": """Create a functional mini-application that demonstrates your full-stack development skills.

**Requirements:**
- Build a specialized tool or utility (NOT a simple calculator)
- Implement proper UI/UX design
- Include frontend and backend components
- Use modern web technologies
- Deploy (optional but recommended)

**Examples of acceptable projects:**
- Task management system
- Weather dashboard with API integration
- E-commerce product catalog
- Social media feed clone
- Real-time chat application
- File upload and sharing system
- Quiz/polling application

**Evaluation Criteria:**
- UI/UX Design (25 points)
- Functionality (25 points)
- Code Quality (25 points)
- Innovation (25 points)

**Submission Requirements:**
1. GitHub repository link (mandatory)
2. Live demo URL (optional but recommended)
3. List of tech stack used
4. Screenshot uploads (minimum 3)

**Deadline:** February 12, 2026 23:59:59""",
        "deadline": "2026-02-12T23:59:59",
        "total_marks": 100,
        "user_project_id": project.id,
        "submission_status": project.submission_status,
        "submitted_at": project.submitted_at
    }
    
    return assignment

# ============== PROJECT SUBMISSION ==============

@router.post("/submit", response_model=Stage2ProjectResponse)
async def submit_project(
    submission: Stage2ProjectSubmit,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit Stage 2 project"""
    # Check eligibility
    check_stage2_eligibility(current_user.id, db)
    
    # Get or create project
    project = db.query(Stage2Project).filter(
        Stage2Project.user_id == current_user.id
    ).first()
    
    if not project:
        project = Stage2Project(user_id=current_user.id)
        db.add(project)
    
    # Update project details
    project.project_title = submission.project_title
    project.project_description = submission.project_description
    project.github_repo_url = submission.github_repo_url
    project.live_demo_url = submission.live_demo_url
    project.tech_stack = submission.tech_stack
    project.submission_status = 'submitted'
    project.submitted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        title="Project Submitted Successfully! 🎉",
        message=f"Your project '{submission.project_title}' has been submitted. Results will be announced soon.",
        type="stage2_submitted"
    )
    db.add(notification)
    db.commit()
    
    # Log activity
    log_activity(db, current_user.id, "stage2_submission", {
        "project_title": submission.project_title,
        "github_url": submission.github_repo_url,
        "tech_stack": submission.tech_stack
    }, request)
    
    return Stage2ProjectResponse.from_orm(project)


# ============== GET PROJECT SUBMISSION ==============

@router.get("/submission", response_model=Stage2ProjectResponse)
async def get_project_submission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's Stage 2 project submission"""
    # Check eligibility
    check_stage2_eligibility(current_user.id, db)
    
    project = db.query(Stage2Project).filter(
        Stage2Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="No project found")
    
    return Stage2ProjectResponse.from_orm(project)


# ============== UPDATE PROJECT ==============

@router.put("/update", response_model=Stage2ProjectResponse)
async def update_project(
    submission: Stage2ProjectSubmit,
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update Stage 2 project (before final submission)"""
    # Check eligibility
    check_stage2_eligibility(current_user.id, db)
    
    project = db.query(Stage2Project).filter(
        Stage2Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="No project found")
    
    # Check if already submitted and evaluated
    if project.total_score is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project has been evaluated. Updates are not allowed."
        )
    
    # Update project
    project.project_title = submission.project_title
    project.project_description = submission.project_description
    project.github_repo_url = submission.github_repo_url
    project.live_demo_url = submission.live_demo_url
    project.tech_stack = submission.tech_stack
    project.submission_status = 'in_progress'
    
    db.commit()
    db.refresh(project)
    
    return Stage2ProjectResponse.from_orm(project)

# ============== STAGE 2 LEADERBOARD ==============

@router.get("/leaderboard")
async def get_stage2_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get Stage 2 leaderboard"""
    projects = db.query(Stage2Project, User).join(User).filter(
        Stage2Project.total_score.isnot(None)
    ).order_by(Stage2Project.total_score.desc()).limit(limit).all()
    
    leaderboard = []
    for idx, (project, user) in enumerate(projects, 1):
        leaderboard.append({
            "rank": idx,
            "user_name": user.full_name,
            "college": user.college_name,
            "project_title": project.project_title,
            "ui_ux_score": float(project.ui_ux_score) if project.ui_ux_score else 0,
            "functionality_score": float(project.functionality_score) if project.functionality_score else 0,
            "code_quality_score": float(project.code_quality_score) if project.code_quality_score else 0,
            "innovation_score": float(project.innovation_score) if project.innovation_score else 0,
            "total_score": float(project.total_score) if project.total_score else 0,
            "is_qualified": project.is_qualified
        })
    
    return leaderboard


# ============== ADMIN: EVALUATE PROJECT (For testing/demo) ==============

@router.post("/evaluate/{project_id}")
async def evaluate_project(
    project_id: int,
    ui_ux_score: float,
    functionality_score: float,
    code_quality_score: float,
    innovation_score: float,
    evaluator_comments: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evaluate a Stage 2 project (Admin/Testing only)"""
    project = db.query(Stage2Project).filter(
        Stage2Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update scores
    project.ui_ux_score = ui_ux_score
    project.functionality_score = functionality_score
    project.code_quality_score = code_quality_score
    project.innovation_score = innovation_score
    project.total_score = ui_ux_score + functionality_score + code_quality_score + innovation_score
    project.evaluator_comments = evaluator_comments
    
    # Determine qualification (e.g., top 10 for finale)
    all_projects = db.query(Stage2Project).filter(
        Stage2Project.total_score.isnot(None)
    ).order_by(Stage2Project.total_score.desc()).all()
    
    for idx, p in enumerate(all_projects, 1):
        p.is_qualified = idx <= 10  # Top 10 qualify for finale
    
    db.commit()
    
    # Send notification
    notification = Notification(
        user_id=project.user_id,
        title="Round 2 Results Announced! 🎉",
        message=f"Your project has been evaluated. Total Score: {project.total_score}/100",
        type="stage2_result"
    )
    db.add(notification)
    db.commit()
    
    return {"status": "success", "total_score": float(project.total_score)}
