import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# ----------------- Auth Schemas -----------------
class UserRegister(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "community_user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ----------------- ML Prediction Schemas -----------------
class PredictRequest(BaseModel):
    ph: float = Field(..., ge=0.0, le=14.0, description="pH level (0-14)")
    turbidity: float = Field(..., ge=0.0, description="Turbidity in NTU")
    tds: float = Field(..., ge=0.0, description="Total Dissolved Solids in ppm")
    temperature: float = Field(..., description="Temperature in Celsius")

class PredictResponse(BaseModel):
    classification: str # Safe, Moderate, Dangerous
    confidence: float # 0 to 100
    confidence_score: float # 0.0 to 1.0
    probabilities: Dict[str, float]
    inputs: Dict[str, float]
    recommendation: str
    treatment_advice: str
    flags: List[str]
    action_steps: List[str]
    status_code: str
    ui_color: str


# ----------------- Water Sources Schemas -----------------
class WaterSourceBase(BaseModel):
    name: str
    source_type: str
    latitude: float
    longitude: float
    address: str
    zone: Optional[str] = "Metro Basin"
    operator: Optional[str] = "Municipal Water Authority"
    contact_phone: Optional[str] = "+1-555-0199"

class WaterSourceCreate(WaterSourceBase):
    current_ph: float = 7.2
    current_turbidity: float = 1.2
    current_tds: float = 180.0
    current_temperature: float = 20.0

class WaterSourceResponse(WaterSourceBase):
    id: int
    current_ph: float
    current_turbidity: float
    current_tds: float
    current_temperature: float
    status: str
    confidence: float
    recommendation: str
    treatment_advice: Optional[str] = ""
    is_active: bool
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}

class WaterSourceNearbyResponse(WaterSourceResponse):
    distance_km: float
    distance_meters: float
    travel_time_walk_mins: int
    is_nearest_safe: bool = False


# ----------------- Historical Readings -----------------
class SensorReadingResponse(BaseModel):
    id: int
    source_id: int
    ph: float
    turbidity: float
    tds: float
    temperature: float
    status: str
    timestamp: datetime.datetime

    model_config = {"from_attributes": True}


# ----------------- Community Reports Schemas -----------------
class CommunityReportCreate(BaseModel):
    source_id: Optional[int] = None
    source_name: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = "Pinned Location"
    category: str
    comments: str
    observed_color: Optional[str] = "Normal"
    observed_odor: Optional[str] = "None"
    observed_taste: Optional[str] = "Untested"
    ph: Optional[float] = None
    turbidity: Optional[float] = None
    tds: Optional[float] = None
    temperature: Optional[float] = None
    photo_url: Optional[str] = None
    reporter_name: Optional[str] = "Community Member"

class CommunityReportResponse(BaseModel):
    id: int
    source_id: Optional[int] = None
    source_name: Optional[str] = None
    latitude: float
    longitude: float
    address: str
    category: str
    comments: str
    observed_color: str
    observed_odor: str
    observed_taste: str
    ph: Optional[float]
    turbidity: Optional[float]
    tds: Optional[float]
    temperature: Optional[float]
    photo_url: Optional[str]
    status: str
    upvotes: int
    reporter_name: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class ReportModerateRequest(BaseModel):
    status: str # "Verified", "Flagged", "Investigating", "Resolved"


# ----------------- Alerts Schemas -----------------
class AlertResponse(BaseModel):
    id: int
    source_id: Optional[int]
    source_name: Optional[str]
    title: str
    message: str
    severity: str
    status: str
    parameters_json: Optional[str]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# ----------------- Analytics & Overview Schemas -----------------
class AnalyticsSummaryResponse(BaseModel):
    total_sources: int
    safe_sources_count: int
    moderate_sources_count: int
    dangerous_sources_count: int
    safe_percentage: float
    active_alerts_count: int
    reports_today_count: int
    total_reports_count: int
    avg_ph: float
    avg_turbidity: float
    avg_tds: float
    avg_temperature: float
    source_type_distribution: Dict[str, int]
    zone_distribution: Dict[str, Dict[str, int]]
