"""
Integration tests for the gaokao-decision-system API.
Run: python -m pytest tests/test_api.py -v
"""
import pytest
from httpx import ASGITransport, AsyncClient
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "1.0.0"


@pytest.mark.anyio
async def test_get_universities(client):
    resp = await client.get("/api/universities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 9
    uni = data[0]
    assert "name" in uni
    assert "level" in uni


@pytest.mark.anyio
async def test_get_universities_filter(client):
    resp = await client.get("/api/universities?level=985")
    assert resp.status_code == 200
    data = resp.json()
    for uni in data:
        assert uni["level"] == "985"


@pytest.mark.anyio
async def test_recommendations_high_score(client):
    """Test recommendation for a high-score student (650)"""
    resp = await client.post("/api/recommendations", json={
        "score": 650,
        "rank": 876,
        "subjects": ["物理", "化学", "生物"],
        "preference_region": ["上海", "北京"],
        "preference_major": ["计算机", "人工智能"],
        "risk_tolerance": "稳健"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    recs = data["recommendations"]
    assert len(recs) > 0
    summary = data["summary"]
    assert summary["冲"] + summary["稳"] + summary["保"] == len(recs)
    # Verify flat structure (not nested)
    r = recs[0]
    assert "university_name" in r
    assert "major" in r
    assert "level" in r
    assert "admission_probability" in r


@pytest.mark.anyio
async def test_recommendations_low_score(client):
    """Test recommendation for a lower-score student (620)"""
    resp = await client.post("/api/recommendations", json={
        "score": 620,
        "rank": 5000,
        "subjects": ["物理", "化学"],
        "preference_region": [],
        "preference_major": [],
        "risk_tolerance": "保守"
    })
    assert resp.status_code == 200
    data = resp.json()
    recs = data["recommendations"]
    # Should have some safety (保) recommendations
    bao = [r for r in recs if r["level"] == "保"]
    assert len(bao) > 0


@pytest.mark.anyio
async def test_recommendations_aggressive(client):
    """Test aggressive risk tolerance"""
    resp = await client.post("/api/recommendations", json={
        "score": 640,
        "rank": 1700,
        "subjects": ["物理", "化学"],
        "preference_region": ["北京"],
        "preference_major": ["计算机"],
        "risk_tolerance": "激进"
    })
    assert resp.status_code == 200
    data = resp.json()
    recs = data["recommendations"]
    chong = [r for r in recs if r["level"] == "冲"]
    assert len(chong) > 0


@pytest.mark.anyio
async def test_score_conversion(client):
    resp = await client.get("/api/score-conversion?score=650")
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 650
    assert data["estimated_rank"] > 0


@pytest.mark.anyio
async def test_yunnan_scores(client):
    resp = await client.get("/api/yunnan/scores?year=2024")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 50  # seeded 54 + 7 rows


@pytest.mark.anyio
async def test_yunnan_scores_filter(client):
    resp = await client.get("/api/yunnan/scores?university_id=beida")
    assert resp.status_code == 200
    data = resp.json()
    for row in data:
        assert row["university_id"] == "beida"


@pytest.mark.anyio
async def test_b_segment_plans(client):
    resp = await client.get("/api/yunnan/b-segment/plans/2025/beida")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 7


@pytest.mark.anyio
async def test_create_volunteer_plan(client):
    uid = f"test-plan-{int(time.time() * 1000)}"
    resp = await client.post("/api/volunteer-plans", json={
        "id": uid,
        "name": "测试志愿方案",
        "student_info": {
            "score": 650,
            "rank": 876,
            "subjects": ["物理"],
            "preference_region": ["北京"],
            "preference_major": ["计算机"],
            "risk_tolerance": "稳健"
        },
        "recommendations": [
            {
                "level": "稳",
                "university_name": "北京大学",
                "university_id": "beida",
                "major": "计算机类",
                "major_code": "0809",
                "min_score": 698,
                "admission_probability": 45.0,
                "suggested_order": 1,
                "school_level": "985"
            }
        ],
        "created_at": "2026-04-27T00:00:00"
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
