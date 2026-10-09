from typing import List, Optional
from datetime import datetime, timedelta
import random
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db
from backend.app.models import WaterSource, SensorReading
from backend.app.schemas import (
    WaterSourceResponse, WaterSourceNearbyResponse, WaterSourceCreate,
    SensorReadingResponse
)
from backend.app.services.geo_service import (
    haversine_distance, calculate_travel_time, generate_route_points
)
from backend.app.services.ml_service import ml_service
from backend.app.services.alert_service import alert_service

router = APIRouter(tags=["Water Sources"])

@router.get("/sources", response_model=List[WaterSourceResponse])
async def list_sources(
    source_type: Optional[str] = Query(None, description="Filter by source type (well, tap, river, tanker, borewell, spring)"),
    status: Optional[str] = Query(None, description="Filter by status (Safe, Moderate, Dangerous)"),
    search: Optional[str] = Query(None, description="Search by name or zone"),
    db: AsyncSession = Depends(get_db)
):
    query = select(WaterSource).where(WaterSource.is_active == True)

    if source_type and source_type.lower() != "all":
        query = query.where(WaterSource.source_type == source_type.lower())

    if status and status.lower() != "all":
        query = query.where(WaterSource.status == status.capitalize())

    if search:
        search_fmt = f"%{search.lower()}%"
        query = query.where(
            (WaterSource.name.ilike(search_fmt)) | 
            (WaterSource.zone.ilike(search_fmt)) |
            (WaterSource.address.ilike(search_fmt))
        )

    query = query.order_by(WaterSource.id.asc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sources/nearby", response_model=List[WaterSourceNearbyResponse])
async def get_nearby_sources(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius: float = Query(15.0, description="Search radius in kilometers"),
    status: Optional[str] = Query(None, description="Filter by status"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns water sources sorted by proximity to the provided lat/lng coordinates.
    """
    query = select(WaterSource).where(WaterSource.is_active == True)
    if source_type and source_type.lower() != "all":
        query = query.where(WaterSource.source_type == source_type.lower())
    if status and status.lower() != "all":
        query = query.where(WaterSource.status == status.capitalize())

    result = await db.execute(query)
    sources = result.scalars().all()

    nearby_list = []
    nearest_safe_id = None
    min_safe_dist = float("inf")

    # First pass: find nearest safe
    for s in sources:
        dist_km = haversine_distance(lat, lng, s.latitude, s.longitude)
        if s.status == "Safe" and dist_km < min_safe_dist:
            min_safe_dist = dist_km
            nearest_safe_id = s.id

    for s in sources:
        dist_km = haversine_distance(lat, lng, s.latitude, s.longitude)
        if dist_km <= radius:
            item = WaterSourceNearbyResponse(
                id=s.id,
                name=s.name,
                source_type=s.source_type,
                latitude=s.latitude,
                longitude=s.longitude,
                address=s.address,
                zone=s.zone,
                operator=s.operator,
                contact_phone=s.contact_phone,
                current_ph=s.current_ph,
                current_turbidity=s.current_turbidity,
                current_tds=s.current_tds,
                current_temperature=s.current_temperature,
                status=s.status,
                confidence=s.confidence,
                recommendation=s.recommendation,
                treatment_advice=s.treatment_advice or "",
                is_active=s.is_active,
                updated_at=s.updated_at,
                distance_km=dist_km,
                distance_meters=round(dist_km * 1000, 1),
                travel_time_walk_mins=calculate_travel_time(dist_km),
                is_nearest_safe=(s.id == nearest_safe_id)
            )
            nearby_list.append(item)

    nearby_list.sort(key=lambda x: x.distance_km)
    return nearby_list


@router.get("/sources/nearest-safe")
async def get_nearest_safe_source(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    db: AsyncSession = Depends(get_db)
):
    """
    Specifically locates the single nearest Safe source, with walking time and routing coordinates.
    """
    result = await db.execute(
        select(WaterSource).where(
            WaterSource.is_active == True,
            WaterSource.status == "Safe"
        )
    )
    safe_sources = result.scalars().all()

    if not safe_sources:
        raise HTTPException(status_code=404, detail="No safe water sources currently found.")

    nearest = None
    min_dist = float("inf")
    for s in safe_sources:
        dist = haversine_distance(lat, lng, s.latitude, s.longitude)
        if dist < min_dist:
            min_dist = dist
            nearest = s

    route = generate_route_points(lat, lng, nearest.latitude, nearest.longitude, steps=6)

    return {
        "source": WaterSourceResponse.model_validate(nearest),
        "distance_km": min_dist,
        "distance_meters": round(min_dist * 1000, 1),
        "travel_time_walk_mins": calculate_travel_time(min_dist),
        "travel_time_drive_mins": max(1, int(round((min_dist / 35.0) * 60))),
        "user_location": [lat, lng],
        "source_location": [nearest.latitude, nearest.longitude],
        "route_coordinates": route
    }


@router.get("/sources/{source_id}", response_model=WaterSourceResponse)
async def get_source_by_id(source_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WaterSource).where(WaterSource.id == source_id))
    source = result.scalars().first()
    if not source:
        raise HTTPException(status_code=404, detail="Water source not found")
    return source


@router.get("/sources/{source_id}/history", response_model=List[SensorReadingResponse])
async def get_source_readings_history(
    source_id: int,
    timeframe: str = Query("7d", description="Timeframe: 24h, 7d, or 30d"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns historical trend logs for a water source.
    """
    now = datetime.utcnow()
    if timeframe == "24h":
        cutoff = now - timedelta(hours=24)
        limit = 24
    elif timeframe == "30d":
        cutoff = now - timedelta(days=30)
        limit = 60
    else: # 7d
        cutoff = now - timedelta(days=7)
        limit = 35

    result = await db.execute(
        select(SensorReading)
        .where(
            SensorReading.source_id == source_id,
            SensorReading.timestamp >= cutoff
        )
        .order_by(SensorReading.timestamp.asc())
        .limit(limit)
    )
    readings = result.scalars().all()
    return readings


@router.post("/sources/{source_id}/simulate-reading")
async def simulate_source_reading(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Simulates a new incoming sensor reading for the source, runs ML prediction,
    updates source status, records historical reading, and fires alert if Dangerous.
    """
    result = await db.execute(select(WaterSource).where(WaterSource.id == source_id))
    source = result.scalars().first()
    if not source:
        raise HTTPException(status_code=404, detail="Water source not found")

    # Introduce slight realistic drift
    ph_drift = random.uniform(-0.15, 0.15)
    turbidity_drift = random.uniform(-0.25, 0.25)
    tds_drift = random.uniform(-10.0, 10.0)
    temp_drift = random.uniform(-0.5, 0.5)

    new_ph = round(max(3.0, min(12.0, source.current_ph + ph_drift)), 2)
    new_turb = round(max(0.1, min(40.0, source.current_turbidity + turbidity_drift)), 2)
    new_tds = round(max(50.0, min(2200.0, source.current_tds + tds_drift)), 1)
    new_temp = round(max(10.0, min(45.0, source.current_temperature + temp_drift)), 1)

    # ML Inference
    pred = ml_service.predict_water_quality(new_ph, new_turb, new_tds, new_temp)

    # Update Source
    source.current_ph = new_ph
    source.current_turbidity = new_turb
    source.current_tds = new_tds
    source.current_temperature = new_temp
    source.status = pred["classification"]
    source.confidence = pred["confidence"]
    source.recommendation = pred["recommendation"]
    source.treatment_advice = pred["treatment_advice"]
    source.updated_at = datetime.utcnow()

    # Log reading
    reading = SensorReading(
        source_id=source.id,
        ph=new_ph,
        turbidity=new_turb,
        tds=new_tds,
        temperature=new_temp,
        status=source.status,
        timestamp=datetime.utcnow()
    )
    db.add(reading)

    # Check alert condition
    triggered_alert = None
    if source.status == "Dangerous":
        triggered_alert = await alert_service.trigger_danger_alert(db, source, pred)

    await db.commit()
    await db.refresh(source)

    return {
        "message": f"Updated {source.name} reading successfully",
        "source": WaterSourceResponse.model_validate(source),
        "prediction": pred,
        "alert_triggered": triggered_alert is not None
    }


@router.post("/sources", response_model=WaterSourceResponse)
async def create_water_source(source_in: WaterSourceCreate, db: AsyncSession = Depends(get_db)):
    pred = ml_service.predict_water_quality(
        source_in.current_ph,
        source_in.current_turbidity,
        source_in.current_tds,
        source_in.current_temperature
    )
    source = WaterSource(
        name=source_in.name,
        source_type=source_in.source_type.lower(),
        latitude=source_in.latitude,
        longitude=source_in.longitude,
        address=source_in.address,
        zone=source_in.zone or "Metro Basin",
        current_ph=source_in.current_ph,
        current_turbidity=source_in.current_turbidity,
        current_tds=source_in.current_tds,
        current_temperature=source_in.current_temperature,
        status=pred["classification"],
        confidence=pred["confidence"],
        recommendation=pred["recommendation"],
        treatment_advice=pred["treatment_advice"],
        operator=source_in.operator or "Community Operator",
        contact_phone=source_in.contact_phone or "+1-555-0100"
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)

    # Add initial reading
    reading = SensorReading(
        source_id=source.id,
        ph=source.current_ph,
        turbidity=source.current_turbidity,
        tds=source.current_tds,
        temperature=source.current_temperature,
        status=source.status,
        timestamp=datetime.utcnow()
    )
    db.add(reading)
    await db.commit()

    return source
