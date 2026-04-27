"""
数据查询 API - 按院校/专业/位次查询历年录取信息
"""
from fastapi import APIRouter, Query
from typing import Optional
from db import get_connection

router = APIRouter(prefix="/api/query", tags=["数据查询"])


@router.get("/by-school")
async def query_by_school(
    university_name: Optional[str] = Query(None, description="院校名称，支持模糊匹配"),
    major: Optional[str] = Query(None, description="专业名称，支持模糊匹配"),
    year: Optional[int] = Query(None, description="招生年份"),
    min_score: Optional[int] = Query(None, description="最低分下限"),
    max_score: Optional[int] = Query(None, description="最低分上限"),
    limit: int = Query(50, ge=1, le=200)
):
    """
    按院校/专业/年份查询录取分数和位次。

    示例:
    - /api/query/by-school?university_name=上海交通
    - /api/query/by-school?major=计算机&year=2024
    - /api/query/by-school?university_name=电子科技&major=通信
    """
    conn = get_connection()
    cursor = conn.cursor()

    conditions = ["1=1"]
    params = []

    if university_name:
        conditions.append("s.university_name LIKE ?")
        params.append(f"%{university_name}%")

    if major:
        conditions.append("s.major_category LIKE ?")
        params.append(f"%{major}%")

    if year:
        conditions.append("s.year = ?")
        params.append(year)

    if min_score is not None:
        conditions.append("s.min_score >= ?")
        params.append(min_score)

    if max_score is not None:
        conditions.append("s.min_score <= ?")
        params.append(max_score)

    where = " AND ".join(conditions)

    cursor.execute(f"""
        SELECT s.university_name, s.university_id, s.major_category, s.major_code,
               s.year, s.enrollment_count, s.min_score, s.max_score, s.avg_score,
               s.min_rank, u.level, u.province, u.city
        FROM yunnan_physics_scores s
        JOIN universities u ON s.university_id = u.id
        WHERE {where}
        ORDER BY s.min_score DESC
        LIMIT ?
    """, params + [limit])

    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "query": {
            "university_name": university_name,
            "major": major,
            "year": year,
        },
        "results": [dict(r) for r in rows]
    }


@router.get("/by-rank")
async def query_by_rank(
    rank: int = Query(..., description="考生位次"),
    year: int = Query(2024, description="招生年份"),
    tolerance: int = Query(500, ge=0, le=5000, description="位次容忍范围（上下浮动）"),
    limit: int = Query(50, ge=1, le=200)
):
    """
    根据位次查询可选院校和专业。
    返回在该位次上下 tolerance 范围内可录取的院校专业。

    示例:
    - /api/query/by-rank?rank=3000&year=2024
    - /api/query/by-rank?rank=1000&year=2024&tolerance=1000
    """
    conn = get_connection()
    cursor = conn.cursor()

    rank_low = max(1, rank - tolerance)
    rank_high = rank + tolerance

    cursor.execute("""
        SELECT s.university_name, s.university_id, s.major_category, s.major_code,
               s.year, s.enrollment_count, s.min_score, s.max_score, s.avg_score,
               s.min_rank, u.level, u.province, u.city,
               CASE
                   WHEN s.min_rank < ? THEN '冲'
                   WHEN s.min_rank BETWEEN ? AND ? THEN '稳'
                   ELSE '保'
               END as tier
        FROM yunnan_physics_scores s
        JOIN universities u ON s.university_id = u.id
        WHERE s.year = ? AND s.min_rank IS NOT NULL
          AND s.min_rank BETWEEN ? AND ?
        ORDER BY s.min_rank
        LIMIT ?
    """, (rank, rank, rank + tolerance, year, rank_low, rank_high, limit))

    rows = cursor.fetchall()
    conn.close()

    results = [dict(r) for r in rows]

    # Summary
    chong = [r for r in results if r["tier"] == "冲"]
    wen = [r for r in results if r["tier"] == "稳"]
    bao = [r for r in results if r["tier"] == "保"]

    return {
        "query": {
            "rank": rank,
            "year": year,
            "tolerance": tolerance,
        },
        "count": len(results),
        "summary": {
            "冲": len(chong),
            "稳": len(wen),
            "保": len(bao),
        },
        "results": results
    }


@router.get("/by-plan")
async def query_by_plan(
    university_name: Optional[str] = Query(None, description="院校名称，支持模糊匹配"),
    university_id: Optional[str] = Query(None, description="院校ID"),
    year: Optional[int] = Query(None, description="招生年份"),
    limit: int = Query(100, ge=1, le=500)
):
    """
    按院校和年份查询本科批B段招生计划。

    示例:
    - /api/query/by-plan?university_name=上海交通&year=2025
    - /api/query/by-plan?university_id=shjd&year=2026
    """
    conn = get_connection()
    cursor = conn.cursor()

    conditions = ["1=1"]
    params = []

    if university_name:
        conditions.append("university_name LIKE ?")
        params.append(f"%{university_name}%")
    if university_id:
        conditions.append("university_id = ?")
        params.append(university_id)
    if year:
        conditions.append("year = ?")
        params.append(year)

    where = " AND ".join(conditions)

    cursor.execute(f"""
        SELECT id, university_id, university_name, year, major_code,
               major_group_sequence, major_group_name, required_subjects,
               major_category, included_majors, tuition, enrollment_count,
               campus, notes, data_source
        FROM yunnan_b_segment_plans
        WHERE {where}
        ORDER BY university_name, major_code
        LIMIT ?
    """, params + [limit])

    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "query": {
            "university_name": university_name,
            "university_id": university_id,
            "year": year,
        },
        "results": [dict(r) for r in rows]
    }


@router.get("/universities-list")
async def list_universities():
    """获取所有有录取数据的院校列表（用于下拉选择）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT s.university_id, s.university_name, u.level, u.province
        FROM yunnan_physics_scores s
        JOIN universities u ON s.university_id = u.id
        ORDER BY u.level, s.university_name
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
