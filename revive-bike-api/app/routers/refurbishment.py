from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Refurbishment, Bike, User, PartUsage, Part, Donation, DonationHistory
from app.schemas import (
    RefurbishmentCreate, RefurbishmentResponse, RefurbishmentUpdate,
    PartUsageCreate, PartUsageResponse, BikeResponse
)
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/api", tags=["翻新工序"])


def add_donation_history(db: Session, donation_id: int, status: str, description: str):
    history = DonationHistory(
        donation_id=donation_id,
        status=status,
        description=description
    )
    db.add(history)
    db.commit()


@router.get("/bikes", response_model=List[BikeResponse])
def list_bikes(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Bike)
    if status:
        query = query.filter(Bike.status == status)
    bikes = query.order_by(Bike.created_at.desc()).offset(skip).limit(limit).all()
    return bikes


@router.get("/bikes/{bike_id}", response_model=BikeResponse)
def get_bike(
    bike_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")
    return bike


@router.post("/refurbishments", response_model=RefurbishmentResponse)
def create_refurbishment(
    refurbishment_in: RefurbishmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("volunteer", "admin"))
):
    bike = db.query(Bike).filter(Bike.id == refurbishment_in.bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    refurbishment = Refurbishment(
        bike_id=refurbishment_in.bike_id,
        volunteer_id=current_user.id,
        stage=refurbishment_in.stage,
        description=refurbishment_in.description,
        notes=refurbishment_in.notes,
        status="in_progress"
    )
    db.add(refurbishment)

    if bike.status == "donated":
        bike.status = "refurbishing"
    db.commit()
    db.refresh(refurbishment)

    donation = db.query(Donation).filter(Donation.bike_id == bike.id).first()
    if donation:
        add_donation_history(db, donation.id, "refurbishing",
                             f"开始翻新 - {refurbishment_in.stage}")

    return refurbishment


@router.get("/refurbishments", response_model=List[RefurbishmentResponse])
def list_refurbishments(
    bike_id: Optional[int] = None,
    status: Optional[str] = None,
    volunteer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Refurbishment)
    if bike_id:
        query = query.filter(Refurbishment.bike_id == bike_id)
    if status:
        query = query.filter(Refurbishment.status == status)
    if volunteer_id:
        query = query.filter(Refurbishment.volunteer_id == volunteer_id)
    refurbishments = query.order_by(Refurbishment.started_at.desc()).offset(skip).limit(limit).all()
    return refurbishments


@router.get("/refurbishments/{refurbishment_id}", response_model=RefurbishmentResponse)
def get_refurbishment(
    refurbishment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    refurbishment = db.query(Refurbishment).filter(Refurbishment.id == refurbishment_id).first()
    if not refurbishment:
        raise HTTPException(status_code=404, detail="Refurbishment not found")
    return refurbishment


@router.put("/refurbishments/{refurbishment_id}", response_model=RefurbishmentResponse)
def update_refurbishment(
    refurbishment_id: int,
    update_in: RefurbishmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("volunteer", "admin"))
):
    refurbishment = db.query(Refurbishment).filter(Refurbishment.id == refurbishment_id).first()
    if not refurbishment:
        raise HTTPException(status_code=404, detail="Refurbishment not found")

    update_data = update_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(refurbishment, key, value)

    if "status" in update_data and update_data["status"] == "completed":
        refurbishment.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(refurbishment)

    return refurbishment


@router.post("/refurbishments/{refurbishment_id}/complete")
def complete_refurbishment(
    refurbishment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("volunteer", "admin"))
):
    refurbishment = db.query(Refurbishment).filter(Refurbishment.id == refurbishment_id).first()
    if not refurbishment:
        raise HTTPException(status_code=404, detail="Refurbishment not found")
    if refurbishment.status == "completed":
        raise HTTPException(status_code=400, detail="Refurbishment already completed")

    refurbishment.status = "completed"
    refurbishment.completed_at = datetime.utcnow()
    db.commit()

    bike = db.query(Bike).filter(Bike.id == refurbishment.bike_id).first()
    if bike:
        all_refurbishments = db.query(Refurbishment).filter(
            Refurbishment.bike_id == bike.id,
            Refurbishment.status == "in_progress"
        ).all()
        if not all_refurbishments:
            bike.status = "refurbished"

            donation = db.query(Donation).filter(Donation.bike_id == bike.id).first()
            if donation:
                add_donation_history(db, donation.id, "refurbished",
                                     f"翻新完成，车辆编号：{bike.bike_code}，等待匹配受赠人")

    db.commit()
    db.refresh(refurbishment)

    return refurbishment


@router.post("/part-usages", response_model=PartUsageResponse)
def create_part_usage(
    usage_in: PartUsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("volunteer", "admin"))
):
    part = db.query(Part).filter(Part.id == usage_in.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    if part.stock_quantity < usage_in.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    bike = db.query(Bike).filter(Bike.id == usage_in.bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    part_usage = PartUsage(
        part_id=usage_in.part_id,
        bike_id=usage_in.bike_id,
        refurbishment_id=usage_in.refurbishment_id,
        quantity=usage_in.quantity,
        notes=usage_in.notes
    )
    db.add(part_usage)

    part.stock_quantity -= usage_in.quantity
    db.commit()
    db.refresh(part_usage)

    return part_usage


@router.get("/bikes/{bike_id}/part-usages", response_model=List[PartUsageResponse])
def list_bike_part_usages(
    bike_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    usages = db.query(PartUsage).filter(PartUsage.bike_id == bike_id).order_by(PartUsage.used_at.desc()).all()
    return usages
