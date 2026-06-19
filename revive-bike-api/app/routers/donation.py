from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Donation, User, Bike, Pickup, DonationHistory
from app.schemas import (
    DonationCreate, DonationResponse, DonationDetailResponse,
    PickupCreate, PickupResponse, DonationHistoryResponse,
    BikeCreate, BikeResponse
)
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/donations", tags=["捐赠回收"])


def add_donation_history(db: Session, donation_id: int, status: str, description: str):
    history = DonationHistory(
        donation_id=donation_id,
        status=status,
        description=description
    )
    db.add(history)
    db.commit()


@router.post("", response_model=DonationResponse)
def create_donation(
    donation_in: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    donation = Donation(
        donor_id=current_user.id,
        description=donation_in.description,
        status="pending"
    )
    db.add(donation)
    db.commit()
    db.refresh(donation)

    add_donation_history(db, donation.id, "pending", "捐赠登记成功，等待预约回收")

    return donation


@router.get("", response_model=List[DonationResponse])
def list_donations(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Donation)
    if current_user.role == "donor":
        query = query.filter(Donation.donor_id == current_user.id)
    if status:
        query = query.filter(Donation.status == status)
    donations = query.order_by(Donation.created_at.desc()).offset(skip).limit(limit).all()
    return donations


@router.get("/{donation_id}", response_model=DonationDetailResponse)
def get_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if current_user.role == "donor" and donation.donor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return donation


@router.get("/{donation_id}/history", response_model=List[DonationHistoryResponse])
def get_donation_history(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if current_user.role == "donor" and donation.donor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    history = db.query(DonationHistory).filter(
        DonationHistory.donation_id == donation_id
    ).order_by(DonationHistory.created_at.asc()).all()
    return history


@router.post("/{donation_id}/schedule-pickup", response_model=PickupResponse)
def schedule_pickup(
    donation_id: int,
    pickup_in: PickupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if current_user.role == "donor" and donation.donor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if donation.status != "pending":
        raise HTTPException(status_code=400, detail="Donation is not in pending status")

    existing_pickup = db.query(Pickup).filter(Pickup.donation_id == donation_id).first()
    if existing_pickup:
        raise HTTPException(status_code=400, detail="Pickup already scheduled")

    pickup = Pickup(
        donation_id=donation_id,
        address=pickup_in.address,
        contact_name=pickup_in.contact_name,
        contact_phone=pickup_in.contact_phone,
        scheduled_date=pickup_in.scheduled_date,
        scheduled_time=pickup_in.scheduled_time,
        notes=pickup_in.notes,
        status="scheduled"
    )
    db.add(pickup)
    db.commit()
    db.refresh(pickup)

    donation.status = "scheduled"
    db.commit()

    add_donation_history(db, donation_id, "scheduled",
                         f"已预约回收，时间：{pickup_in.scheduled_date} {pickup_in.scheduled_time or ''}")

    return pickup


@router.get("/pickups/list", response_model=List[PickupResponse])
def list_pickups(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("volunteer", "admin"))
):
    query = db.query(Pickup)
    if status:
        query = query.filter(Pickup.status == status)
    pickups = query.order_by(Pickup.scheduled_date.asc()).offset(skip).limit(limit).all()
    return pickups


@router.post("/pickups/{pickup_id}/assign")
def assign_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("volunteer", "admin"))
):
    pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")
    if pickup.status != "scheduled":
        raise HTTPException(status_code=400, detail="Pickup is not in scheduled status")

    pickup.volunteer_id = current_user.id
    pickup.status = "assigned"
    db.commit()
    db.refresh(pickup)

    donation = db.query(Donation).filter(Donation.id == pickup.donation_id).first()
    if donation:
        donation.status = "assigned"
        add_donation_history(db, donation.id, "assigned", f"志愿者 {current_user.full_name or current_user.username} 已接单")
        db.commit()

    return pickup


@router.post("/pickups/{pickup_id}/complete")
def complete_pickup(
    pickup_id: int,
    bike_in: BikeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("volunteer", "admin"))
):
    pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")
    if pickup.status not in ["scheduled", "assigned"]:
        raise HTTPException(status_code=400, detail="Pickup cannot be completed")
    if pickup.volunteer_id and pickup.volunteer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this volunteer")

    donation = db.query(Donation).filter(Donation.id == pickup.donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    bike_code = f"BK{datetime.now().strftime('%Y%m%d')}{donation.id:04d}"
    bike = Bike(
        bike_code=bike_code,
        brand=bike_in.brand,
        model=bike_in.model,
        color=bike_in.color,
        bike_type=bike_in.bike_type,
        frame_size=bike_in.frame_size,
        condition_on_receipt=bike_in.condition_on_receipt,
        status="donated",
        received_at=datetime.utcnow()
    )
    db.add(bike)
    db.commit()
    db.refresh(bike)

    donation.bike_id = bike.id
    donation.status = "received"
    db.commit()

    pickup.status = "completed"
    pickup.completed_at = datetime.utcnow()
    db.commit()

    add_donation_history(db, donation.id, "received",
                         f"已回收成功，车辆编号：{bike_code}，进入翻新流程")

    return {"pickup": pickup, "bike": bike}
