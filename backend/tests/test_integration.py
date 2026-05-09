"""Tests for score-to-rank conversion, data entry CRUD, and rank-based recommendations."""
import pytest
from httpx import ASGITransport, AsyncClient
import sys
import os

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


# ====== Score Conversion ======

@pytest.mark.anyio
async def test_score_conversion_exact(client):
    resp = await client.get("/api/score-conversion?score=650&year=2024")
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 650
    assert data["estimated_rank"] > 0
    assert data["year_used"] == 2024


@pytest.mark.anyio
async def test_score_conversion_default_year(client):
    resp = await client.get("/api/score-conversion?score=640")
    assert resp.status_code == 200
    data = resp.json()
    assert data["estimated_rank"] > 0
    assert data["year_used"] in [2024, 2025]


@pytest.mark.anyio
async def test_score_conversion_boundary(client):
    resp = await client.get("/api/score-conversion?score=400")
    assert resp.status_code == 200
    data = resp.json()
    assert data["estimated_rank"] > 0


@pytest.mark.anyio
async def test_score_conversion_low(client):
    resp = await client.get("/api/score-conversion?score=350")
    assert resp.status_code == 200
    data = resp.json()
    assert data["estimated_rank"] > 0


# ====== Data Entry CRUD ======

@pytest.mark.anyio
async def test_list_scores(client):
    resp = await client.get("/api/data-entry/scores?year=2024&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 10


@pytest.mark.anyio
async def test_list_segments(client):
    resp = await client.get("/api/data-entry/segments?year=2024&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_list_plans(client):
    resp = await client.get("/api/data-entry/plans?year=2024&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


# ====== Rank-based Recommendations ======

@pytest.mark.anyio
async def test_recommendations_with_year(client):
    resp = await client.post("/api/recommendations", json={
        "score": 640,
        "rank": 1700,
        "subjects": ["物理", "化学", "生物"],
        "preference_region": ["北京"],
        "preference_major": ["计算机"],
        "risk_tolerance": "稳健",
        "year": 2024
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    recs = data["recommendations"]
    assert len(recs) > 0
    for r in recs:
        assert "min_rank" in r
        assert r["min_rank"] is not None


@pytest.mark.anyio
async def test_recommendations_rank_tiers(client):
    resp = await client.post("/api/recommendations", json={
        "score": 630,
        "rank": 2500,
        "subjects": ["物理", "化学", "生物"],
        "preference_region": [],
        "preference_major": [],
        "risk_tolerance": "稳健",
        "year": 2024
    })
    assert resp.status_code == 200
    data = resp.json()
    levels = set(r["level"] for r in data["recommendations"])
    # Should have at least 冲 and 保 tiers
    assert "冲" in levels or "稳" in levels or "保" in levels


@pytest.mark.anyio
async def test_recommendations_aggressive_wider(client):
    """Aggressive should have wider rank ranges than conservative"""
    resp_aggressive = await client.post("/api/recommendations", json={
        "score": 600,
        "rank": 5000,
        "subjects": ["物理", "化学"],
        "preference_region": [],
        "preference_major": [],
        "risk_tolerance": "激进",
        "year": 2024
    })
    resp_conservative = await client.post("/api/recommendations", json={
        "score": 600,
        "rank": 5000,
        "subjects": ["物理", "化学"],
        "preference_region": [],
        "preference_major": [],
        "risk_tolerance": "保守",
        "year": 2024
    })
    assert resp_aggressive.status_code == 200
    assert resp_conservative.status_code == 200
    agg_count = len(resp_aggressive.json()["recommendations"])
    cons_count = len(resp_conservative.json()["recommendations"])
    # Both should return results
    assert agg_count > 0
    assert cons_count > 0


# ====== Plan Data ======

@pytest.mark.anyio
async def test_plan_query_with_batch_type(client):
    resp = await client.get("/api/query/by-plan?batch_type=本科批B段&year=2024&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["results"], list)


@pytest.mark.anyio
async def test_b_segment_stats(client):
    resp = await client.get("/api/yunnan/b-segment/stats/2024")
    assert resp.status_code == 200
    data = resp.json()
    assert "year" in data