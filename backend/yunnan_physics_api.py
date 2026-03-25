# 云南省物理类招生分数线 API 接口
# 添加到 backend/main.py 中

from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
import sqlite3
import json
import os

router = APIRouter(prefix="/api/yunnan", tags=["云南物理类招生数据"])

# 数据模型
class AdmissionScore(BaseModel):
    """招生分数线数据模型"""
    id: int
    university_id: str
    university_name: str
    year: int
    major_category: str
    major_code: Optional[str]
    enrollment_count: Optional[int]
    max_score: Optional[int]
    min_score: int
    avg_score: Optional[int]
    min_rank: Optional[int]
    notes: Optional[str]

class ScoreQueryParams(BaseModel):
    """查询参数"""
    year: Optional[int] = 2024                    # 年份
    min_score: Optional[int] = None               # 最低分下限
    max_score: Optional[int] = None               # 最高分上限
    university_id: Optional[str] = None           # 学校ID
    major_category: Optional[str] = None          # 专业大类

# 数据库连接辅助函数
def get_db_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'gaokao.db')
    return sqlite3.connect(db_path)

# API 接口 1: 获取所有招生分数线数据
@router.get("/scores", response_model=List[AdmissionScore])
async def get_admission_scores(
    year: Optional[int] = 2024,
    university_id: Optional[str] = None,
    major_category: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None
):
    """
    获取云南省物理类招生分数线数据
    
    示例:
    - /api/yunnan/scores?year=2024
    - /api/yunnan/scores?university_id=beida
    - /api/yunnan/scores?min_score=700&max_score=720
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM yunnan_physics_scores WHERE year = ?"
    params = [year]
    
    if university_id:
        query += " AND university_id = ?"
        params.append(university_id)
    
    if major_category:
        query += " AND major_category LIKE ?"
        params.append(f"%{major_category}%")
    
    if min_score:
        query += " AND min_score >= ?"
        params.append(min_score)
    
    if max_score:
        query += " AND min_score <= ?"
        params.append(max_score)
    
    query += " ORDER BY min_score DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# API 接口 2: 根据考生分数推荐学校
@router.get("/recommend")
async def recommend_universities(score: int, rank: Optional[int] = None, year: int = 2024):
    """
    根据考生分数推荐可报考的学校和专业
    
    参数:
    - score: 考生分数
    - rank: 考生位次（可选）
    - year: 招生年份
    
    返回:
    - 冲: 分数略高的学校（+5分以内）
    - 稳: 分数匹配的学校（±5分）
    - 保: 分数有把握的学校（-5分以下）
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 冲: 分数略高（+1到+10分）
    cursor.execute('''
        SELECT *, '冲' as level FROM yunnan_physics_scores 
        WHERE year = ? AND min_score > ? AND min_score <= ? + 10
        ORDER BY min_score ASC
    ''', (year, score, score))
    chong = [dict(row) for row in cursor.fetchall()]
    
    # 稳: 分数匹配（±5分）
    cursor.execute('''
        SELECT *, '稳' as level FROM yunnan_physics_scores 
        WHERE year = ? AND min_score >= ? - 5 AND min_score <= ? + 5
        ORDER BY min_score DESC
    ''', (year, score, score))
    wen = [dict(row) for row in cursor.fetchall()]
    
    # 保: 分数有把握（-5分以下）
    cursor.execute('''
        SELECT *, '保' as level FROM yunnan_physics_scores 
        WHERE year = ? AND min_score < ? - 5
        ORDER BY min_score DESC LIMIT 20
    ''', (year, score))
    bao = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "考生分数": score,
        "考生位次": rank,
        "招生年份": year,
        "推荐结果": {
            "冲": chong,
            "稳": wen,
            "保": bao
        }
    }

# API 接口 3: 获取学校详情
@router.get("/university/{university_id}")
async def get_university_detail(university_id: str, year: int = 2024):
    """
    获取某学校在云南物理类的所有招生专业详情
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取学校基本信息
    cursor.execute('''
        SELECT * FROM universities WHERE id = ?
    ''', (university_id,))
    university = cursor.fetchone()
    
    # 获取招生分数线
    cursor.execute('''
        SELECT * FROM yunnan_physics_scores 
        WHERE university_id = ? AND year = ?
        ORDER BY min_score DESC
    ''', (university_id, year))
    scores = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    if not university:
        return {"error": "学校不存在"}
    
    return {
        "学校信息": dict(university),
        "招生数据": scores
    }

# API 接口 4: 获取数据统计
@router.get("/statistics")
async def get_statistics(year: int = 2024):
    """
    获取云南省物理类招生数据统计
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 统计信息
    cursor.execute('''
        SELECT 
            COUNT(*) as total_majors,
            COUNT(DISTINCT university_id) as total_universities,
            MIN(min_score) as lowest_score,
            MAX(min_score) as highest_score,
            AVG(min_score) as avg_score,
            SUM(enrollment_count) as total_enrollment
        FROM yunnan_physics_scores 
        WHERE year = ?
    ''', (year,))
    stats = cursor.fetchone()
    
    # 分数段分布
    cursor.execute('''
        SELECT 
            CASE 
                WHEN min_score >= 700 THEN '700分以上'
                WHEN min_score >= 680 THEN '680-699分'
                WHEN min_score >= 660 THEN '660-679分'
                WHEN min_score >= 640 THEN '640-659分'
                ELSE '640分以下'
            END as score_range,
            COUNT(*) as count
        FROM yunnan_physics_scores 
        WHERE year = ?
        GROUP BY score_range
        ORDER BY min_score DESC
    ''', (year,))
    distribution = cursor.fetchall()
    
    conn.close()
    
    return {
        "年份": year,
        "科类": "物理类",
        "省份": "云南",
        "总体统计": {
            "专业数量": stats[0],
            "学校数量": stats[1],
            "最低分": stats[2],
            "最高分": stats[3],
            "平均分": round(stats[4], 2) if stats[4] else None,
            "总招生人数": stats[5] or 0
        },
        "分数段分布": [{"分数段": row[0], "专业数": row[1]} for row in distribution]
    }

# 在 main.py 中添加路由
# app.include_router(yunnan_physics_router)
