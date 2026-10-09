import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="community_user") # "admin" or "community_user"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    reports = relationship("CommunityReport", back_populates="user")


class WaterSource(Base):
    __tablename__ = "water_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    source_type = Column(String(50), index=True, nullable=False) # well, tap, river, tanker, borewell, spring
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500), nullable=False)
    zone = Column(String(100), default="Metro Basin")
    
    # Current sensor readings
    current_ph = Column(Float, default=7.2)
    current_turbidity = Column(Float, default=1.5)
    current_tds = Column(Float, default=180.0)
    current_temperature = Column(Float, default=20.0)
    
    # ML Classification & Status
    status = Column(String(50), default="Safe") # Safe, Moderate, Dangerous
    confidence = Column(Float, default=98.5)
    recommendation = Column(Text, default="Safe for consumption.")
    treatment_advice = Column(Text, default="No special treatment required.")
    
    operator = Column(String(255), default="Municipal Water Dept")
    contact_phone = Column(String(50), default="+1-555-0199")
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    readings = relationship("SensorReading", back_populates="source", cascade="all, delete-orphan")
    reports = relationship("CommunityReport", back_populates="source")
    alerts = relationship("Alert", back_populates="source")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("water_sources.id"), nullable=False, index=True)
    ph = Column(Float, nullable=False)
    turbidity = Column(Float, nullable=False)
    tds = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    status = Column(String(50), default="Safe")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    source = relationship("WaterSource", back_populates="readings")


class CommunityReport(Base):
    __tablename__ = "community_reports"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("water_sources.id"), nullable=True)
    source_name = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500), default="User Pinned Location")
    category = Column(String(100), nullable=False) # Industrial Runoff, Algal Bloom, Sewage, Discoloration/Odor, Chemical Spill, Pipe Break
    comments = Column(Text, nullable=False)
    
    observed_color = Column(String(100), default="Normal")
    observed_odor = Column(String(100), default="None")
    observed_taste = Column(String(100), default="Untested")
    
    # Optional sensor measurements if tested by user
    ph = Column(Float, nullable=True)
    turbidity = Column(Float, nullable=True)
    tds = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    
    photo_url = Column(String(500), nullable=True)
    status = Column(String(50), default="Pending Review") # Pending Review, Verified, Investigating, Resolved, Flagged
    upvotes = Column(Integer, default=1)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter_name = Column(String(255), default="Community Member")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    source = relationship("WaterSource", back_populates="reports")
    user = relationship("User", back_populates="reports")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("water_sources.id"), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="warning") # critical, warning, info
    status = Column(String(50), default="active") # active, acknowledged, resolved
    source_name = Column(String(255), nullable=True)
    parameters_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    source = relationship("WaterSource", back_populates="alerts")
