from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = "donor"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class DonationBase(BaseModel):
    description: Optional[str] = None


class DonationCreate(DonationBase):
    pass


class DonationResponse(DonationBase):
    id: int
    donor_id: int
    bike_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DonationDetailResponse(DonationResponse):
    donor: Optional[UserResponse] = None


class DonationHistoryResponse(BaseModel):
    id: int
    donation_id: int
    status: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class PickupBase(BaseModel):
    address: str
    contact_name: str
    contact_phone: str
    scheduled_date: date
    scheduled_time: Optional[str] = None
    notes: Optional[str] = None


class PickupCreate(PickupBase):
    donation_id: int


class PickupResponse(PickupBase):
    id: int
    donation_id: int
    volunteer_id: Optional[int] = None
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BikeBase(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    bike_type: Optional[str] = None
    frame_size: Optional[str] = None


class BikeCreate(BikeBase):
    condition_on_receipt: Optional[str] = None


class BikeResponse(BikeBase):
    id: int
    bike_code: str
    condition_on_receipt: Optional[str] = None
    status: str
    received_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PartBase(BaseModel):
    name: str
    category: Optional[str] = None
    sku: Optional[str] = None
    stock_quantity: int = 0
    unit: str = "个"
    description: Optional[str] = None


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    stock_quantity: Optional[int] = None
    unit: Optional[str] = None
    description: Optional[str] = None


class PartResponse(PartBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PartUsageBase(BaseModel):
    part_id: int
    quantity: int = 1
    notes: Optional[str] = None


class PartUsageCreate(PartUsageBase):
    bike_id: int
    refurbishment_id: Optional[int] = None


class PartUsageResponse(PartUsageBase):
    id: int
    bike_id: int
    refurbishment_id: Optional[int] = None
    used_at: datetime
    part: Optional[PartResponse] = None

    class Config:
        from_attributes = True


class RefurbishmentBase(BaseModel):
    bike_id: int
    stage: str
    description: Optional[str] = None
    notes: Optional[str] = None


class RefurbishmentCreate(RefurbishmentBase):
    pass


class RefurbishmentUpdate(BaseModel):
    stage: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    labor_hours: Optional[float] = None
    notes: Optional[str] = None


class RefurbishmentResponse(RefurbishmentBase):
    id: int
    volunteer_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    labor_hours: float
    part_usages: List[PartUsageResponse] = []

    class Config:
        from_attributes = True


class RecipientBase(BaseModel):
    full_name: str
    phone: str
    id_card: Optional[str] = None
    address: Optional[str] = None
    applicant_type: str
    organization: Optional[str] = None
    reason: str
    bike_type_preference: Optional[str] = None
    frame_size_preference: Optional[str] = None


class RecipientCreate(RecipientBase):
    pass


class RecipientResponse(RecipientBase):
    id: int
    applicant_id: int
    status: str
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MatchBase(BaseModel):
    bike_id: int
    recipient_id: int
    notes: Optional[str] = None


class MatchCreate(MatchBase):
    pass


class MatchResponse(MatchBase):
    id: int
    matched_by: Optional[int] = None
    match_date: datetime
    delivery_date: Optional[date] = None
    status: str
    delivered_at: Optional[datetime] = None
    bike: Optional[BikeResponse] = None
    recipient: Optional[RecipientResponse] = None

    class Config:
        from_attributes = True


class TraceResponse(BaseModel):
    donation: DonationResponse
    donation_history: List[DonationHistoryResponse] = []
    bike: Optional[BikeResponse] = None
    pickup: Optional[PickupResponse] = None
    refurbishments: List[RefurbishmentResponse] = []
    part_usages: List[PartUsageResponse] = []
    match: Optional[MatchResponse] = None
