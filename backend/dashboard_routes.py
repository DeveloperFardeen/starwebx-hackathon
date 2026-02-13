from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Stage1Result, Stage2Project, Notification
from schemas import DashboardResponse, UserResponse
from auth_routes import get_current_user
from datetime import date

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard with stage status and results"""
    
    # Get Stage 1 result
    stage1_result = db.query(Stage1Result).filter(
        Stage1Result.user_id == current_user.id
    ).first()
    
    stage1_status = "live"
    if stage1_result and stage1_result.completed_at:
        stage1_status = "completed"
    if date.today() > date.fromisoformat('2026-02-08'):
        stage1_status = "ended"
    now = datetime.now()
    special_start = datetime(2026, 2, 14, 10, 0, 0)
    special_end = datetime(2026, 2, 14, 15, 0, 0)
    
    if special_start <= now <= special_end:
        stage1_status = "live" 
    
    # Get Stage 2 project
    stage2_project = db.query(Stage2Project).filter(
        Stage2Project.user_id == current_user.id
    ).first()
    
    stage2_status = "locked"
    if stage1_result and stage1_result.is_qualified:
        if stage2_project and stage2_project.submitted_at:
            stage2_status = "submitted"
        else:
            stage2_status = "available"
    if date.today() < date.fromisoformat('2026-02-08'):
        stage2_status = "coming-soon"
    if date.today() > date.fromisoformat('2026-02-12'):
        stage2_status = "ended"
   
    # Get unread notifications count
    notifications_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return DashboardResponse(
        user=UserResponse.from_orm(current_user),
        stage1_status=stage1_status,
        stage1_result=stage1_result,
        stage2_status=stage2_status,
        stage2_project=stage2_project,
        notifications_count=notifications_count
    )
