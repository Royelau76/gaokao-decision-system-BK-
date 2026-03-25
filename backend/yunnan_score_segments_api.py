# 云南省物理类一分一段 API 接口
# 添加到 backend/yunnan_physics_api.py 中

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sqlite3
import os

router = APIRouter(prefix="/api/yunnan/segments", tags=["云南物理类一分一段"])

# 数据模型
class ScoreSegment(BaseModel):
    """一分一段数据模型"""
    id: int
    year: int
    score: int
    count: int
    cumulative_count: int
    notes: Optional[str]

class RankQueryResult(BaseModel):
    """位次查询结果"""
    score: int
    year: int
    rank: int
    same_score_count: int
    message: str

# 数据库连接辅助函数
def get_db_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'gaokao.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# API 接口 1: 获取某年的一分一段数据
@router.get("/{year}", response_model=List[ScoreSegment])
async def get_score_segments(year: int, min_score: Optional[int] = None, max_score: Optional[int] = None):
    """
    获取某年云南省物理类一分一段数据
    
    示例:
    - /api/yunnan/segments/2024
    - /api/yunnan/segments/2024?min_score=600&max_score=700
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM yunnan_physics_score_segments WHERE year = ?"
    params = [year]
    
    if min_score:
        query += " AND score >= ?"
        params.append(min_score)
    
    if max_score:
        query += " AND score <= ?"
        params.append(max_score)
    
    query += " ORDER BY score DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail=f"未找到{year}年的一分一段数据")
    
    return [dict(row) for row in rows]

# API 接口 2: 根据分数查询位次
@router.get("/rank/{year}/{score}", response_model=RankQueryResult)
async def get_rank_by_score(year: int, score: int):
    """
    根据分数查询位次
    
    示例:
    - /api/yunnan/segments/rank/2024/650
    
    返回:
    - 该分数对应的累计位次
    - 同分人数
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT score, cumulative_count, count 
        FROM yunnan_physics_score_segments 
        WHERE year = ? AND score = ?
    ''', (year, score))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        # 如果没有精确匹配，查找最接近的分数
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT score, cumulative_count, count 
            FROM yunnan_physics_score_segments 
            WHERE year = ? AND score <= ?
            ORDER BY score DESC LIMIT 1
        ''', (year, score))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"未找到{year}年分数{score}附近的数据")
        
        return {
            "score": row['score'],
            "year": year,
            "rank": row['cumulative_count'],
            "same_score_count": row['count'],
            "message": f"精确分数{score}无数据，显示最接近的较低分数{row['score']}的位次"
        }
    
    return {
        "score": score,
        "year": year,
        "rank": row['cumulative_count'],
        "same_score_count": row['count'],
        "message": f"{year}年{score}分的位次为{row['cumulative_count']}，同分{row['count']}人"
    }

# API 接口 3: 根据位次查询分数
@router.get("/score/{year}/{rank}")
async def get_score_by_rank(year: int, rank: int):
    """
    根据位次查询对应的分数
    
    示例:
    - /api/yunnan/segments/score/2024/1000
    
    返回:
    - 该位次对应的分数
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT score, cumulative_count, count 
        FROM yunnan_physics_score_segments 
        WHERE year = ? AND cumulative_count >= ?
        ORDER BY cumulative_count ASC LIMIT 1
    ''', (year, rank))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"未找到{year}年位次{rank}附近的数据")
    
    return {
        "year": year,
        "rank": rank,
        "score": row['score'],
        "cumulative_count": row['cumulative_count'],
        "message": f"{year}年位次{rank}对应的分数约为{row['score']}分"
    }

# API 接口 4: 获取某年的统计信息
@router.get("/stats/{year}")
async def get_segment_stats(year: int):
    """
    获取某年一分一段数据统计信息
    
    返回:
    - 最高分、最低分
    - 总人数
    - 分数段分布
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 基本统计
    cursor.execute('''
        SELECT 
            MAX(score) as max_score,
            MIN(score) as min_score,
            SUM(count) as total_students,
            MAX(cumulative_count) as max_rank
        FROM yunnan_physics_score_segments 
        WHERE year = ?
    ''', (year,))
    
    stats = cursor.fetchone()
    
    # 分数段分布
    cursor.execute('''
        SELECT 
            CASE 
                WHEN score >= 650 THEN '650分以上'
                WHEN score >= 600 THEN '600-649分'
                WHEN score >= 550 THEN '550-599分'
                WHEN score >= 500 THEN '500-549分'
                ELSE '500分以下'
            END as score_range,
            SUM(count) as count
        FROM yunnan_physics_score_segments 
        WHERE year = ?
        GROUP BY score_range
        ORDER BY MIN(score) DESC
    ''', (year,))
    
    distribution = cursor.fetchall()
    conn.close()
    
    if not stats['max_score']:
        raise HTTPException(status_code=404, detail=f"未找到{year}年的一分一段数据")
    
    return {
        "year": year,
        "最高分": stats['max_score'],
        "最低分": stats['min_score'],
        "总人数": stats['total_students'],
        "最大位次": stats['max_rank'],
        "分数段分布": [{"分数段": row['score_range'], "人数": row['count']} for row in distribution]
    }

# API 接口 5: 对比两年的数据
@router.get("/compare/{year1}/{year2}")
async def compare_years(year1: int, year2: int, score: int):
    """
    对比两年同一分数的位次变化
    
    示例:
    - /api/yunnan/segments/compare/2024/2025/650
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    result = {}
    
    for year in [year1, year2]:
        cursor.execute('''
            SELECT score, cumulative_count, count 
            FROM yunnan_physics_score_segments 
            WHERE year = ? AND score = ?
        ''', (year, score))
        
        row = cursor.fetchone()
        if row:
            result[str(year)] = {
                "score": row['score'],
                "位次": row['cumulative_count'],
                "同分人数": row['count']
            }
        else:
            result[str(year)] = None
    
    conn.close()
    
    if not result[str(year1)] and not result[str(year2)]:
        raise HTTPException(status_code=404, detail=f"未找到{year1}或{year2}年分数{score}的数据")
    
    return {
        "对比分数": score,
        "年份1": year1,
        "年份2": year2,
        "数据": result,
        "说明": f"{score}分在{year1}年和{year2}年的位次对比"
    }
