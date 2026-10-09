"""
AquaShield AI - Comprehensive Seed Data Generator
Populates:
- Admin and Community demo users
- 24 realistic Water Sources across demo geographic region
- 7-day Historical Sensor Readings for each source
- Realistic Crowdsourced Community Reports (with upvotes & statuses)
- Active Emergency & Warning Alerts
- Saves JSON export to /data/sample_sources.json
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
import random

# Ensure repository root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.app.database import engine, Base, AsyncSessionLocal
from backend.app.models import User, WaterSource, SensorReading, CommunityReport, Alert
from backend.app.auth import get_password_hash
from ml.predict import get_predictor

SOURCES_DATA = [
    {
        "name": "Barton Springs Natural Reserve Outlet",
        "source_type": "spring",
        "latitude": 30.2638,
        "longitude": -97.7712,
        "address": "2201 Barton Springs Rd, Austin, TX",
        "zone": "South Hills Reserve",
        "ph": 7.42, "turbidity": 0.45, "tds": 165.0, "temperature": 18.2,
        "operator": "Barton Springs Nature Protection Council",
        "contact_phone": "+1-512-555-0101"
    },
    {
        "name": "Zilker Metropolitan Public Tap Station",
        "source_type": "tap",
        "latitude": 30.2670,
        "longitude": -97.7730,
        "address": "2100 Barton Springs Rd, Austin, TX",
        "zone": "Central Basin",
        "ph": 7.35, "turbidity": 0.60, "tds": 185.0, "temperature": 19.5,
        "operator": "Municipal Water Utility Dept",
        "contact_phone": "+1-512-555-0102"
    },
    {
        "name": "Lady Bird Lake - North Bank Intake",
        "source_type": "river",
        "latitude": 30.2585,
        "longitude": -97.7450,
        "address": "Lady Bird Lake Trail North, Austin, TX",
        "zone": "Central Basin",
        "ph": 7.50, "turbidity": 3.80, "tds": 240.0, "temperature": 21.0,
        "operator": "River Basin Authority",
        "contact_phone": "+1-512-555-0103"
    },
    {
        "name": "Eastside Deep Aquifer Borewell #1",
        "source_type": "borewell",
        "latitude": 30.2612,
        "longitude": -97.7120,
        "address": "2800 E 7th St, Austin, TX",
        "zone": "Eastern Sub-Basin",
        "ph": 7.28, "turbidity": 1.10, "tds": 290.0, "temperature": 20.1,
        "operator": "East Austin Community Water Cooperative",
        "contact_phone": "+1-512-555-0104"
    },
    {
        "name": "South Congress Community Well",
        "source_type": "well",
        "latitude": 30.2450,
        "longitude": -97.7510,
        "address": "1600 S Congress Ave, Austin, TX",
        "zone": "South Hills Reserve",
        "ph": 7.32, "turbidity": 1.30, "tds": 210.0, "temperature": 19.8,
        "operator": "South Austin Water Trust",
        "contact_phone": "+1-512-555-0105"
    },
    {
        "name": "Civic Center Emergency Water Tanker #3",
        "source_type": "tanker",
        "latitude": 30.2655,
        "longitude": -97.7490,
        "address": "301 W 2nd St, Austin, TX",
        "zone": "Central Basin",
        "ph": 7.20, "turbidity": 0.50, "tds": 140.0, "temperature": 18.0,
        "operator": "City Emergency Disaster Response",
        "contact_phone": "+1-512-555-0106"
    },
    {
        "name": "Colorado River Industrial Drainage Canal",
        "source_type": "river",
        "latitude": 30.2520,
        "longitude": -97.6950,
        "address": "River Crossing Way & Industrial Rd, Austin, TX",
        "zone": "Industrial Fringe",
        "ph": 4.10, "turbidity": 18.5, "tds": 1450.0, "temperature": 29.5,
        "operator": "Regional Environmental Enforcement",
        "contact_phone": "+1-512-555-0107"
    },
    {
        "name": "North Lamar Old Well (Mineral Hardness)",
        "source_type": "well",
        "latitude": 30.3020,
        "longitude": -97.7280,
        "address": "4800 N Lamar Blvd, Austin, TX",
        "zone": "North Sector",
        "ph": 7.85, "turbidity": 5.20, "tds": 760.0, "temperature": 23.5,
        "operator": "North District Ground Utility",
        "contact_phone": "+1-512-555-0108"
    },
    {
        "name": "Deep Eddy Artesian Spring",
        "source_type": "spring",
        "latitude": 30.2780,
        "longitude": -97.7735,
        "address": "401 Deep Eddy Ave, Austin, TX",
        "zone": "Central Basin",
        "ph": 7.30, "turbidity": 0.70, "tds": 175.0, "temperature": 18.4,
        "operator": "Artesian Heritage Trust",
        "contact_phone": "+1-512-555-0109"
    },
    {
        "name": "University Quad Hydration Tap",
        "source_type": "tap",
        "latitude": 30.2860,
        "longitude": -97.7390,
        "address": "2400 Speedway, Austin, TX",
        "zone": "University District",
        "ph": 7.15, "turbidity": 0.35, "tds": 155.0, "temperature": 17.8,
        "operator": "Campus Facility Management",
        "contact_phone": "+1-512-555-0110"
    },
    {
        "name": "Shoal Creek Storm Runoff Culvert",
        "source_type": "river",
        "latitude": 30.2810,
        "longitude": -97.7510,
        "address": "Shoal Creek Trail at 24th St, Austin, TX",
        "zone": "University District",
        "ph": 5.60, "turbidity": 24.0, "tds": 980.0, "temperature": 27.2,
        "operator": "Watershed Protection Dept",
        "contact_phone": "+1-512-555-0111"
    },
    {
        "name": "Mueller Eco-Park Public Filtration Tap",
        "source_type": "tap",
        "latitude": 30.2980,
        "longitude": -97.7050,
        "address": "4550 Mueller Blvd, Austin, TX",
        "zone": "Eastern Sub-Basin",
        "ph": 7.25, "turbidity": 0.40, "tds": 160.0, "temperature": 18.5,
        "operator": "Eco-District Management",
        "contact_phone": "+1-512-555-0112"
    },
    {
        "name": "Montopolis Silt Sedimentation Pond",
        "source_type": "well",
        "latitude": 30.2320,
        "longitude": -97.7020,
        "address": "1200 Montopolis Dr, Austin, TX",
        "zone": "Industrial Fringe",
        "ph": 6.30, "turbidity": 7.80, "tds": 680.0, "temperature": 25.8,
        "operator": "Southeast Community Watch",
        "contact_phone": "+1-512-555-0113"
    },
    {
        "name": "Travis Heights Heritage Well",
        "source_type": "well",
        "latitude": 30.2480,
        "longitude": -97.7390,
        "address": "1100 Travis Heights Blvd, Austin, TX",
        "zone": "South Hills Reserve",
        "ph": 7.38, "turbidity": 1.20, "tds": 220.0, "temperature": 19.4,
        "operator": "South Austin Water Trust",
        "contact_phone": "+1-512-555-0114"
    },
    {
        "name": "Rainey District Tanker Depot",
        "source_type": "tanker",
        "latitude": 30.2590,
        "longitude": -97.7380,
        "address": "80 Rainey St, Austin, TX",
        "zone": "Central Basin",
        "ph": 7.22, "turbidity": 0.55, "tds": 170.0, "temperature": 18.8,
        "operator": "Municipal Water Utility Dept",
        "contact_phone": "+1-512-555-0115"
    },
    {
        "name": "Chemical Wash Spill Site - Airport Blvd",
        "source_type": "borewell",
        "latitude": 30.3080,
        "longitude": -97.6890,
        "address": "6200 Airport Blvd, Austin, TX",
        "zone": "Industrial Fringe",
        "ph": 10.80, "turbidity": 14.5, "tds": 1620.0, "temperature": 31.0,
        "operator": "State Hazard Remediation Unit",
        "contact_phone": "+1-512-555-0116"
    },
    {
        "name": "Westlake Mountain Spring Well",
        "source_type": "spring",
        "latitude": 30.2790,
        "longitude": -97.8010,
        "address": "3300 Bee Caves Rd, Austin, TX",
        "zone": "Upland Hills",
        "ph": 7.45, "turbidity": 0.30, "tds": 130.0, "temperature": 16.5,
        "operator": "Westlake Aquifer Conservation",
        "contact_phone": "+1-512-555-0117"
    },
    {
        "name": "Rollingwood Deep Borewell #2",
        "source_type": "borewell",
        "latitude": 30.2680,
        "longitude": -97.7950,
        "address": "403 Nixon Dr, Austin, TX",
        "zone": "Upland Hills",
        "ph": 7.35, "turbidity": 0.85, "tds": 195.0, "temperature": 19.0,
        "operator": "Rollingwood Public Works",
        "contact_phone": "+1-512-555-0118"
    },
    {
        "name": "Highland Mall Community Borewell",
        "source_type": "borewell",
        "latitude": 30.3270,
        "longitude": -97.7140,
        "address": "6001 Airport Blvd, Austin, TX",
        "zone": "North Sector",
        "ph": 7.24, "turbidity": 1.40, "tds": 245.0, "temperature": 20.4,
        "operator": "Metro Transit Authority Hydration",
        "contact_phone": "+1-512-555-0119"
    },
    {
        "name": "Boggy Creek Urban Drainage Outfall",
        "source_type": "river",
        "latitude": 30.2720,
        "longitude": -97.7010,
        "address": "1114 Nile St, Austin, TX",
        "zone": "Eastern Sub-Basin",
        "ph": 8.70, "turbidity": 6.80, "tds": 840.0, "temperature": 27.5,
        "operator": "Watershed Protection Dept",
        "contact_phone": "+1-512-555-0120"
    },
    {
        "name": "Riverside Transit Station Tap",
        "source_type": "tap",
        "latitude": 30.2410,
        "longitude": -97.7250,
        "address": "2101 E Riverside Dr, Austin, TX",
        "zone": "Eastern Sub-Basin",
        "ph": 7.28, "turbidity": 0.65, "tds": 190.0, "temperature": 19.2,
        "operator": "Transit Authority Water Dept",
        "contact_phone": "+1-512-555-0121"
    },
    {
        "name": "Balcones Woods Shallow Mineral Well",
        "source_type": "well",
        "latitude": 30.3420,
        "longitude": -97.7420,
        "address": "11200 Balcones Woods Dr, Austin, TX",
        "zone": "North Sector",
        "ph": 7.75, "turbidity": 4.80, "tds": 590.0, "temperature": 22.8,
        "operator": "Northern Hills Water Corp",
        "contact_phone": "+1-512-555-0122"
    },
    {
        "name": "Colorado River South Bend Tap",
        "source_type": "tap",
        "latitude": 30.2510,
        "longitude": -97.7210,
        "address": "Pleasant Valley Park, Austin, TX",
        "zone": "Eastern Sub-Basin",
        "ph": 7.30, "turbidity": 0.80, "tds": 178.0, "temperature": 19.8,
        "operator": "Parks & Recreation Water Services",
        "contact_phone": "+1-512-555-0123"
    },
    {
        "name": "Barton Creek Greenbelt Trailhead Spring",
        "source_type": "spring",
        "latitude": 30.2530,
        "longitude": -97.7940,
        "address": "3755 S Capital of Texas Hwy, Austin, TX",
        "zone": "South Hills Reserve",
        "ph": 7.38, "turbidity": 0.50, "tds": 150.0, "temperature": 17.5,
        "operator": "Greenbelt Naturalist Alliance",
        "contact_phone": "+1-512-555-0124"
    }
]

REPORTS_DATA = [
    {
        "source_name": "Colorado River Industrial Drainage Canal",
        "latitude": 30.2520,
        "longitude": -97.6950,
        "address": "Near Industrial Rd Culvert",
        "category": "Industrial Runoff",
        "comments": "Strong chemical pungent smell and iridescent slick visible on surface. Dead minnows spotted near bank.",
        "observed_color": "Yellowish oily film",
        "observed_odor": "Strong chemical/solvent",
        "observed_taste": "Not tasted - hazardous",
        "ph": 4.2, "turbidity": 17.0, "tds": 1400.0, "temperature": 29.0,
        "status": "Verified",
        "upvotes": 14,
        "reporter_name": "Marcus Vance (Eco-Watch volunteer)"
    },
    {
        "source_name": "Shoal Creek Storm Runoff Culvert",
        "latitude": 30.2810,
        "longitude": -97.7510,
        "address": "Shoal Creek near 24th St Bridge",
        "category": "Sewage Overflow",
        "comments": "Murky grey wastewater backflowing into the creek following yesterday's storm. Avoid pet access.",
        "observed_color": "Murky grey/brown",
        "observed_odor": "Sewage / Rotten organic",
        "observed_taste": "Untested",
        "ph": 5.8, "turbidity": 22.0, "tds": 950.0, "temperature": 26.5,
        "status": "Investigating",
        "upvotes": 8,
        "reporter_name": "Elena Rostova (Trail Runner)"
    },
    {
        "source_name": "Chemical Wash Spill Site - Airport Blvd",
        "latitude": 30.3080,
        "longitude": -97.6890,
        "address": "Airport Blvd Commercial Park Drainage",
        "category": "Chemical Spill",
        "comments": "Foaming white discharge entering ground borewell intake area. Strong bleach odor.",
        "observed_color": "Foamy white/cloudy",
        "observed_odor": "Chlorine / Alkaline caustic",
        "observed_taste": "Untested",
        "ph": 10.5, "turbidity": 13.0, "tds": 1550.0, "temperature": 30.0,
        "status": "Verified",
        "upvotes": 19,
        "reporter_name": "David Miller (Local Resident)"
    },
    {
        "source_name": "North Lamar Old Well",
        "latitude": 30.3020,
        "longitude": -97.7280,
        "address": "4800 N Lamar Blvd Community Garden",
        "category": "Discoloration / Odor",
        "comments": "Water leaves reddish chalky mineral deposits on irrigation fittings. High mineral hardness.",
        "observed_color": "Slight orange-yellow tint",
        "observed_odor": "Metallic/Earthy",
        "observed_taste": "Bitter/Salty mineral",
        "ph": 7.9, "turbidity": 5.0, "tds": 750.0, "temperature": 23.0,
        "status": "Pending Review",
        "upvotes": 4,
        "reporter_name": "Amina Patel"
    },
    {
        "source_name": "Eastside Community Standpipe",
        "latitude": 30.2640,
        "longitude": -97.7180,
        "address": "Comal St & 6th St Intersection",
        "category": "Broken Infrastructure",
        "comments": "Pressure drop and brief brown sediment burst after nearby construction drilling.",
        "observed_color": "Temporary brown silt",
        "observed_odor": "None",
        "observed_taste": "Normal",
        "ph": 7.3, "turbidity": 3.5, "tds": 230.0, "temperature": 19.5,
        "status": "Pending Review",
        "upvotes": 2,
        "reporter_name": "Carlos Gomez"
    },
    {
        "source_name": "Barton Springs Natural Outlet",
        "latitude": 30.2638,
        "longitude": -97.7712,
        "address": "Barton Springs Main Pool",
        "category": "Discoloration / Odor",
        "comments": "Annual algae bloom near shallow edges. Water is clear in central deep basin.",
        "observed_color": "Clear with edge green moss",
        "observed_odor": "Natural spring",
        "observed_taste": "Clean",
        "ph": 7.4, "turbidity": 0.8, "tds": 170.0, "temperature": 18.0,
        "status": "Resolved",
        "upvotes": 11,
        "reporter_name": "Jennifer Wu"
    }
]

async def seed_all():
    print("Beginning AquaShield AI database seeding...")
    predictor = get_predictor()

    async with engine.begin() as conn:
        # Recreate tables fresh
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Seed Users
        admin_user = User(
            email="admin@aquashield.org",
            name="AquaShield Admin",
            hashed_password=get_password_hash("password123"),
            role="admin",
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        community_user = User(
            email="citizen@aquashield.org",
            name="Sarah Chen (Community Member)",
            hashed_password=get_password_hash("password123"),
            role="community_user",
            created_at=datetime.utcnow() - timedelta(days=20)
        )
        session.add_all([admin_user, community_user])
        await session.flush()

        # 2. Seed Water Sources + Historical Readings
        created_sources = []
        now = datetime.utcnow()

        for s_data in SOURCES_DATA:
            # Predict status
            pred = predictor.predict(
                ph=s_data["ph"],
                turbidity=s_data["turbidity"],
                tds=s_data["tds"],
                temperature=s_data["temperature"]
            )

            source = WaterSource(
                name=s_data["name"],
                source_type=s_data["source_type"],
                latitude=s_data["latitude"],
                longitude=s_data["longitude"],
                address=s_data["address"],
                zone=s_data["zone"],
                current_ph=s_data["ph"],
                current_turbidity=s_data["turbidity"],
                current_tds=s_data["tds"],
                current_temperature=s_data["temperature"],
                status=pred["classification"],
                confidence=pred["confidence"],
                recommendation=pred["recommendation"],
                treatment_advice=pred["treatment_advice"],
                operator=s_data["operator"],
                contact_phone=s_data["contact_phone"],
                is_active=True,
                updated_at=now
            )
            session.add(source)
            await session.flush()
            created_sources.append(source)

            # Generate 7 days of historical readings (every 6 hours = 28 points)
            for i in range(28, 0, -1):
                reading_time = now - timedelta(hours=i * 6)
                # Small random variation
                h_ph = round(s_data["ph"] + random.uniform(-0.12, 0.12), 2)
                h_turb = round(max(0.1, s_data["turbidity"] + random.uniform(-0.25, 0.25)), 2)
                h_tds = round(max(40.0, s_data["tds"] + random.uniform(-15.0, 15.0)), 1)
                h_temp = round(s_data["temperature"] + random.uniform(-1.0, 1.0), 1)

                h_reading = SensorReading(
                    source_id=source.id,
                    ph=h_ph,
                    turbidity=h_turb,
                    tds=h_tds,
                    temperature=h_temp,
                    status=source.status,
                    timestamp=reading_time
                )
                session.add(h_reading)

            # Create Alert if Dangerous or critical
            if pred["classification"] == "Dangerous":
                alert = Alert(
                    source_id=source.id,
                    source_name=source.name,
                    title=f"CRITICAL SAFETY WARNING: {source.name}",
                    message=f"Dangerous contamination detected at {source.name}. Classification: Dangerous ({pred['confidence']} confidence). Recommendation: {pred['recommendation']}",
                    severity="critical",
                    status="active",
                    parameters_json=json.dumps(pred["inputs"]),
                    created_at=now - timedelta(hours=random.randint(1, 12))
                )
                session.add(alert)
            elif pred["classification"] == "Moderate" and random.random() < 0.5:
                alert = Alert(
                    source_id=source.id,
                    source_name=source.name,
                    title=f"Water Quality Notice: {source.name}",
                    message=f"Sub-optimal readings observed at {source.name}. Boiling or micro-filtration advised prior to consumption.",
                    severity="warning",
                    status="active",
                    parameters_json=json.dumps(pred["inputs"]),
                    created_at=now - timedelta(hours=random.randint(4, 24))
                )
                session.add(alert)

        # 3. Seed Community Reports
        for r_data in REPORTS_DATA:
            report = CommunityReport(
                source_name=r_data["source_name"],
                latitude=r_data["latitude"],
                longitude=r_data["longitude"],
                address=r_data["address"],
                category=r_data["category"],
                comments=r_data["comments"],
                observed_color=r_data["observed_color"],
                observed_odor=r_data["observed_odor"],
                observed_taste=r_data["observed_taste"],
                ph=r_data.get("ph"),
                turbidity=r_data.get("turbidity"),
                tds=r_data.get("tds"),
                temperature=r_data.get("temperature"),
                status=r_data["status"],
                upvotes=r_data["upvotes"],
                user_id=community_user.id,
                reporter_name=r_data["reporter_name"],
                created_at=now - timedelta(hours=random.randint(2, 48))
            )
            session.add(report)

        await session.commit()

        # 4. Save sample JSON export to data/sample_sources.json
        os.makedirs(os.path.join(REPO_ROOT, "data"), exist_ok=True)
        export_path = os.path.join(REPO_ROOT, "data", "sample_sources.json")
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(SOURCES_DATA, f, indent=2)

        print(f"Successfully seeded {len(created_sources)} water sources!")
        print(f"Created {len(REPORTS_DATA)} community reports and active alerts.")
        print(f"Exported sources to {export_path}")

if __name__ == "__main__":
    asyncio.run(seed_all())
