from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Part, User
from app.schemas import PartCreate, PartResponse, PartUpdate
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/parts", tags=["零件管理"])


@router.post("", response_model=PartResponse)
def create_part(
    part_in: PartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "volunteer"))
):
    if part_in.sku:
        existing = db.query(Part).filter(Part.sku == part_in.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="SKU already exists")

    part = Part(**part_in.dict())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


@router.get("", response_model=List[PartResponse])
def list_parts(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    low_stock: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Part)
    if category:
        query = query.filter(Part.category == category)
    if keyword:
        query = query.filter(Part.name.contains(keyword))
    if low_stock:
        query = query.filter(Part.stock_quantity < 10)
    parts = query.order_by(Part.created_at.desc()).offset(skip).limit(limit).all()
    return parts


@router.get("/{part_id}", response_model=PartResponse)
def get_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part


@router.put("/{part_id}", response_model=PartResponse)
def update_part(
    part_id: int,
    update_in: PartUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "volunteer"))
):
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    update_data = update_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(part, key, value)

    db.commit()
    db.refresh(part)
    return part


@router.delete("/{part_id}")
def delete_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    db.delete(part)
    db.commit()
    return {"message": "Part deleted successfully"}
