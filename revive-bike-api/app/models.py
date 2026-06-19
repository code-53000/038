from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Date, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    role = Column(String(20), nullable=False, default="donor")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donations = relationship("Donation", back_populates="donor", foreign_keys="Donation.donor_id")
    pickups_as_volunteer = relationship("Pickup", back_populates="volunteer", foreign_keys="Pickup.volunteer_id")
    refurbishments = relationship("Refurbishment", back_populates="volunteer")
    recipient_applications = relationship("Recipient", back_populates="applicant")


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    description = Column(Text)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donor = relationship("User", back_populates="donations", foreign_keys=[donor_id])
    bike = relationship("Bike", back_populates="donation")
    pickup = relationship("Pickup", back_populates="donation", uselist=False)
    donation_history = relationship("DonationHistory", back_populates="donation")


class DonationHistory(Base):
    __tablename__ = "donation_history"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"), nullable=False)
    status = Column(String(20), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    donation = relationship("Donation", back_populates="donation_history")


class Bike(Base):
    __tablename__ = "bikes"

    id = Column(Integer, primary_key=True, index=True)
    bike_code = Column(String(50), unique=True, index=True, nullable=False)
    brand = Column(String(100))
    model = Column(String(100))
    color = Column(String(50))
    bike_type = Column(String(50))
    frame_size = Column(String(20))
    condition_on_receipt = Column(Text)
    status = Column(String(20), nullable=False, default="donated")
    received_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donation = relationship("Donation", back_populates="bike")
    refurbishments = relationship("Refurbishment", back_populates="bike")
    part_usages = relationship("PartUsage", back_populates="bike")
    match = relationship("Match", back_populates="bike", uselist=False)


class Pickup(Base):
    __tablename__ = "pickups"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"), nullable=False, unique=True)
    volunteer_id = Column(Integer, ForeignKey("users.id"))
    address = Column(String(255), nullable=False)
    contact_name = Column(String(100), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(String(20))
    status = Column(String(20), nullable=False, default="scheduled")
    notes = Column(Text)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donation = relationship("Donation", back_populates="pickup")
    volunteer = relationship("User", back_populates="pickups_as_volunteer")


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    sku = Column(String(50), unique=True, index=True)
    stock_quantity = Column(Integer, default=0)
    unit = Column(String(20), default="个")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    part_usages = relationship("PartUsage", back_populates="part")


class PartUsage(Base):
    __tablename__ = "part_usages"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    bike_id = Column(Integer, ForeignKey("bikes.id"), nullable=False)
    refurbishment_id = Column(Integer, ForeignKey("refurbishments.id"))
    quantity = Column(Integer, nullable=False, default=1)
    notes = Column(Text)
    used_at = Column(DateTime, default=datetime.utcnow)

    part = relationship("Part", back_populates="part_usages")
    bike = relationship("Bike", back_populates="part_usages")
    refurbishment = relationship("Refurbishment", back_populates="part_usages")


class Refurbishment(Base):
    __tablename__ = "refurbishments"

    id = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stage = Column(String(50), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default="in_progress")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    labor_hours = Column(Float, default=0)
    notes = Column(Text)

    bike = relationship("Bike", back_populates="refurbishments")
    volunteer = relationship("User", back_populates="refurbishments")
    part_usages = relationship("PartUsage", back_populates="refurbishment")


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    id_card = Column(String(50))
    address = Column(String(255))
    applicant_type = Column(String(50), nullable=False)
    organization = Column(String(100))
    reason = Column(Text, nullable=False)
    bike_type_preference = Column(String(50))
    frame_size_preference = Column(String(20))
    status = Column(String(20), nullable=False, default="pending")
    review_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = relationship("User", back_populates="recipient_applications")
    matches = relationship("Match", back_populates="recipient")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"), nullable=False, unique=True)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=False)
    matched_by = Column(Integer, ForeignKey("users.id"))
    match_date = Column(DateTime, default=datetime.utcnow)
    delivery_date = Column(Date)
    status = Column(String(20), nullable=False, default="matched")
    notes = Column(Text)
    delivered_at = Column(DateTime)

    bike = relationship("Bike", back_populates="match")
    recipient = relationship("Recipient", back_populates="matches")
