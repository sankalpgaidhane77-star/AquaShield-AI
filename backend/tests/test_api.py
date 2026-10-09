import pytest
from httpx import AsyncClient, ASGITransport
import os
import sys

# Ensure repository root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"
from backend.app.main import app

@pytest.mark.asyncio
async def test_predict_endpoint_safe():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "ph": 7.3,
            "turbidity": 0.8,
            "tds": 150.0,
            "temperature": 19.0
        }
        response = await client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["classification"] == "Safe"
        assert data["confidence"] > 80.0
        assert "recommendation" in data
        assert data["status_code"] == "safe"

@pytest.mark.asyncio
async def test_predict_endpoint_dangerous():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "ph": 3.8,
            "turbidity": 22.0,
            "tds": 1400.0,
            "temperature": 32.0
        }
        response = await client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["classification"] == "Dangerous"
        assert "DANGEROUS" in data["recommendation"]

@pytest.mark.asyncio
async def test_get_sources():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/sources")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 20

@pytest.mark.asyncio
async def test_get_nearby_sources():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Austin downtown coords
        response = await client.get("/sources/nearby?lat=30.2672&lng=-97.7431&radius=10.0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "distance_km" in data[0]
        assert "travel_time_walk_mins" in data[0]

@pytest.mark.asyncio
async def test_nearest_safe_locator():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/sources/nearest-safe?lat=30.2672&lng=-97.7431")
        assert response.status_code == 200
        data = response.json()
        assert data["source"]["status"] == "Safe"
        assert "route_coordinates" in data
        assert len(data["route_coordinates"]) > 2

@pytest.mark.asyncio
async def test_community_reports_and_upvote():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. List reports
        list_res = await client.get("/reports")
        assert list_res.status_code == 200
        reports = list_res.json()
        assert len(reports) > 0

        # 2. Submit new report
        new_report = {
            "source_name": "Test Point Creek",
            "latitude": 30.255,
            "longitude": -97.760,
            "category": "Algal Bloom",
            "comments": "Green surface scum observed in eddy.",
            "observed_color": "Green film",
            "reporter_name": "Test Tester"
        }
        create_res = await client.post("/reports", json=new_report)
        assert create_res.status_code == 200
        created = create_res.json()
        assert created["category"] == "Algal Bloom"

        # 3. Upvote
        upvote_res = await client.post(f"/api/reports/{created['id']}/upvote")
        assert upvote_res.status_code == 200
        assert upvote_res.json()["upvotes"] == 2

@pytest.mark.asyncio
async def test_alerts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/alerts")
        assert res.status_code == 200
        alerts = res.json()
        assert isinstance(alerts, list)

@pytest.mark.asyncio
async def test_analytics_summary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_sources"] >= 20
        assert "safe_percentage" in data
        assert "source_type_distribution" in data
