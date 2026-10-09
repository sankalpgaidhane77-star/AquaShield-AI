import os
import shutil
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db
from backend.app.models import CommunityReport, User
from backend.app.schemas import (
    CommunityReportCreate, CommunityReportResponse, ReportModerateRequest
)
from backend.app.auth import get_current_user, get_current_admin
from backend.app.config import settings

router = APIRouter(tags=["Community Reports"])

@router.get("/reports", response_model=List[CommunityReportResponse])
async def list_reports(
    status: Optional[str] = Query(None, description="Filter by status (Pending Review, Verified, Flagged, Resolved)"),
    category: Optional[str] = Query(None, description="Filter by contamination category"),
    db: AsyncSession = Depends(get_db)
):
    query = select(CommunityReport)
    if status and status.lower() != "all":
        query = query.where(CommunityReport.status == status)
    if category and category.lower() != "all":
        query = query.where(CommunityReport.category == category)

    query = query.order_by(desc(CommunityReport.created_at))
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/reports", response_model=CommunityReportResponse)
async def create_report(
    report_in: CommunityReportCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new crowdsourced water quality contamination report.
    """
    reporter_name = report_in.reporter_name or "Community Member"
    user_id = None
    if current_user:
        reporter_name = current_user.name
        user_id = current_user.id

    report = CommunityReport(
        source_id=report_in.source_id,
        source_name=report_in.source_name or "Custom Pinned Location",
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        address=report_in.address or "Observed Location",
        category=report_in.category,
        comments=report_in.comments,
        observed_color=report_in.observed_color or "Normal",
        observed_odor=report_in.observed_odor or "None",
        observed_taste=report_in.observed_taste or "Untested",
        ph=report_in.ph,
        turbidity=report_in.turbidity,
        tds=report_in.tds,
        temperature=report_in.temperature,
        photo_url=report_in.photo_url,
        status="Pending Review",
        upvotes=1,
        user_id=user_id,
        reporter_name=reporter_name,
        created_at=datetime.utcnow()
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.post("/reports/{report_id}/upvote")
async def upvote_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """
    Upvote or corroborate a community report to increase trust score.
    Automatically marks report as 'Verified' if upvotes reach 3.
    """
    result = await db.execute(select(CommunityReport).where(CommunityReport.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.upvotes += 1
    if report.upvotes >= 3 and report.status == "Pending Review":
        report.status = "Verified"

    await db.commit()
    await db.refresh(report)
    return {
        "message": "Report upvoted / verified successfully",
        "report_id": report.id,
        "upvotes": report.upvotes,
        "status": report.status
    }


@router.patch("/reports/{report_id}/status", response_model=CommunityReportResponse)
async def moderate_report_status(
    report_id: int,
    mod_data: ReportModerateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Admin moderation queue: Update status to 'Verified', 'Investigating', 'Resolved', or 'Flagged'.
    """
    result = await db.execute(select(CommunityReport).where(CommunityReport.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = mod_data.status
    await db.commit()
    await db.refresh(report)
    return report


@router.post("/reports/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    """
    Accepts photo evidence upload and saves to local upload folder.
    """
    allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Invalid image file extension")

    file_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"photo_url": f"/uploads/{file_name}", "filename": file_name}
