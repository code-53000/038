from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recipient, User, Match, Bike, Donation, DonationHistory, Refurbishment, PartUsage
from app.schemas import (
    RecipientCreate, RecipientResponse,
    MatchCreate, MatchResponse,
    TraceResponse
)
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/api", tags=["受赠匹配"])


def add_donation_history(db: Session, donation_id: int, status: str, description: str):
    history = DonationHistory(
        donation_id=donation_id,
        status=status,
        description=description
    )
    db.add(history)
    db.commit()


@router.post("/recipients", response_model=RecipientResponse)
def create_recipient(
    recipient_in: RecipientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipient = Recipient(
        applicant_id=current_user.id,
        **recipient_in.dict()
    )
    db.add(recipient)
    db.commit()
    db.refresh(recipient)
    return recipient


@router.get("/recipients", response_model=List[RecipientResponse])
def list_recipients(
    status: Optional[str] = None,
    applicant_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Recipient)
    if current_user.role not in ["admin", "volunteer"]:
        query = query.filter(Recipient.applicant_id == current_user.id)
    if status:
        query = query.filter(Recipient.status == status)
    if applicant_type:
        query = query.filter(Recipient.applicant_type == applicant_type)
    recipients = query.order_by(Recipient.created_at.desc()).offset(skip).limit(limit).all()
    return recipients


@router.get("/recipients/{recipient_id}", response_model=RecipientResponse)
def get_recipient(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if current_user.role not in ["admin", "volunteer"] and recipient.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return recipient


@router.post("/recipients/{recipient_id}/approve")
def approve_recipient(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "volunteer"))
):
    recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if recipient.status != "pending":
        raise HTTPException(status_code=400, detail="Recipient is not in pending status")

    recipient.status = "approved"
    db.commit()
    db.refresh(recipient)
    return recipient


@router.post("/recipients/{recipient_id}/reject")
def reject_recipient(
    recipient_id: int,
    review_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "volunteer"))
):
    recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if recipient.status != "pending":
        raise HTTPException(status_code=400, detail="Recipient is not in pending status")

    recipient.status = "rejected"
    recipient.review_notes = review_notes
    db.commit()
    db.refresh(recipient)
    return recipient


@router.post("/matches", response_model=MatchResponse)
def create_match(
    match_in: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "volunteer"))
):
    bike = db.query(Bike).filter(Bike.id == match_in.bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")
    if bike.status != "refurbished":
        raise HTTPException(status_code=400, detail="Bike is not available for matching")

    recipient = db.query(Recipient).filter(Recipient.id == match_in.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if recipient.status != "approved":
        raise HTTPException(status_code=400, detail="Recipient is not approved")

    existing_match = db.query(Match).filter(Match.bike_id == match_in.bike_id).first()
    if existing_match:
        raise HTTPException(status_code=400, detail="Bike already matched")

    match = Match(
        bike_id=match_in.bike_id,
        recipient_id=match_in.recipient_id,
        matched_by=current_user.id,
        notes=match_in.notes,
        status="matched"
    )
    db.add(match)

    bike.status = "matched"
    recipient.status = "matched"
    db.commit()
    db.refresh(match)

    donation = db.query(Donation).filter(Donation.bike_id == bike.id).first()
    if donation:
        add_donation_history(db, donation.id, "matched",
                             f"已匹配给受赠人：{recipient.full_name}")

    return match


@router.get("/matches", response_model=List[MatchResponse])
def list_matches(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Match)
    if status:
        query = query.filter(Match.status == status)
    matches = query.order_by(Match.match_date.desc()).offset(skip).limit(limit).all()
    return matches


@router.get("/matches/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.post("/matches/{match_id}/deliver")
def deliver_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "volunteer"))
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.status != "matched":
        raise HTTPException(status_code=400, detail="Match is not in matched status")

    match.status = "delivered"
    match.delivered_at = datetime.utcnow()
    db.commit()

    bike = db.query(Bike).filter(Bike.id == match.bike_id).first()
    if bike:
        bike.status = "donated_completed"

    recipient = db.query(Recipient).filter(Recipient.id == match.recipient_id).first()
    if recipient:
        recipient.status = "received"

    donation = db.query(Donation).filter(Donation.bike_id == match.bike_id).first()
    if donation:
        donation.status = "completed"
        add_donation_history(db, donation.id, "completed",
                             f"车辆已交付给受赠人，捐赠完成！")

    db.commit()
    db.refresh(match)
    return match


@router.get("/trace/{donation_id}", response_model=TraceResponse)
def trace_donation(
    donation_id: int,
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    history = db.query(DonationHistory).filter(
        DonationHistory.donation_id == donation_id
    ).order_by(DonationHistory.created_at.asc()).all()

    bike = None
    pickup = None
    refurbishments = []
    part_usages = []
    match = None

    if donation.bike_id:
        bike = db.query(Bike).filter(Bike.id == donation.bike_id).first()
        pickup = db.query(Donation).filter(Donation.id == donation_id).first().pickup
        refurbishments = db.query(Refurbishment).filter(
            Refurbishment.bike_id == donation.bike_id
        ).order_by(Refurbishment.started_at.asc()).all()
        part_usages = db.query(PartUsage).filter(
            PartUsage.bike_id == donation.bike_id
        ).order_by(PartUsage.used_at.asc()).all()
        match = db.query(Match).filter(Match.bike_id == donation.bike_id).first()

    return TraceResponse(
        donation=donation,
        donation_history=history,
        bike=bike,
        pickup=pickup,
        refurbishments=refurbishments,
        part_usages=part_usages,
        match=match
    )
