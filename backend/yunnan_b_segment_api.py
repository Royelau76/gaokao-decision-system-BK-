# 云南省物理类本科批B段招生计划 API 接口
# 添加到 backend/yunnan_physics_api.py 或单独文件

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import json

from db import get_connection

router = APIRouter(prefix="/api/yunnan/b-segment", tags=["云南物理类本科批B段"])

# 数据模型
class BSegmentPlan(BaseModel):
    """本科批B段招生计划数据模型"""
    id: int
    year: int
    university_id: str
    university_name: str
    major_code: str                        # 专业代号
    major_group_sequence: Optional[str] = None  # 专业组序号
    major_group_name: Optional[str] = None
    required_subjects: Optional[str] = None
    major_category: str
    included_majors: Optional[str] = None
    tuition: Optional[int] = None
    enrollment_count: int
    campus: Optional[str] = None
    notes: Optional[str] = None

# API 接口 1: 获取某年某校的B段招生计划
@router.get("/plans/{year}/{university_id}", response_model=List[BSegmentPlan])
async def get_b_segment_plans(year: int, university_id: str):
    """
    获取某学校某年的本科批B段招生计划
    
    示例:
    - /api/yunnan/b-segment/plans/2025/beida
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM yunnan_b_segment_plans
        WHERE year = ? AND university_id = ?
        ORDER BY major_code
    ''', (year, university_id))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail=f"未找到{year}年{university_id}的B段招生计划")
    
    return [dict(row) for row in rows]

# API 接口 2: 按选考科目筛选
@router.get("/plans/by-subject/{year}")
async def get_plans_by_subject(year: int, subject: str, university_id: Optional[str] = None):
    """
    按选考科目筛选B段招生计划
    
    示例:
    - /api/yunnan/b-segment/plans/by-subject/2025?subject=化学
    - /api/yunnan/b-segment/plans/by-subject/2025?subject=化学&university_id=beida
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT * FROM yunnan_b_segment_plans 
        WHERE year = ? AND required_subjects LIKE ?
    '''
    params = [year, f'%{subject}%']
    
    if university_id:
        query += " AND university_id = ?"
        params.append(university_id)
    
    query += " ORDER BY university_id, major_code"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# API 接口 3: 按专业组代码查询
@router.get("/plans/by-code/{year}/{university_id}/{major_code}")
async def get_plan_by_code(year: int, university_id: str, major_code: str):
    """
    查询具体专业组代码的B段招生计划

    示例:
    - /api/yunnan/b-segment/plans/by-code/2025/beida/01
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM yunnan_b_segment_plans
        WHERE year = ? AND university_id = ? AND major_code = ?
    ''', (year, university_id, major_code))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"未找到该专业代号信息")
    
    return dict(row)

# API 接口 4: 获取某年所有B段招生学校列表
@router.get("/universities/{year}")
async def get_b_segment_universities(year: int):
    """
    获取某年所有有B段招生的学校列表
    
    示例:
    - /api/yunnan/b-segment/universities/2025
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT university_id, university_name,
               SUM(enrollment_count) as total_enrollment
        FROM yunnan_b_segment_plans 
        WHERE year = ?
        GROUP BY university_id, university_name
        ORDER BY total_enrollment DESC
    ''', (year,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "university_id": row['university_id'],
        "university_name": row['university_name'],
        "total_enrollment": row['total_enrollment']
    } for row in rows]

# API 接口 5: 统计信息
@router.get("/stats/{year}")
async def get_b_segment_stats(year: int):
    """
    获取某年B段招生计划统计信息
    
    示例:
    - /api/yunnan/b-segment/stats/2025
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 总体统计
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT university_id) as university_count,
            COUNT(*) as total_majors,
            SUM(enrollment_count) as total_enrollment,
            AVG(tuition) as avg_tuition
        FROM yunnan_b_segment_plans 
        WHERE year = ?
    ''', (year,))
    
    stats = cursor.fetchone()
    
    # 按选考科目统计
    cursor.execute('''
        SELECT required_subjects, COUNT(*) as count, SUM(enrollment_count) as enrollment
        FROM yunnan_b_segment_plans 
        WHERE year = ?
        GROUP BY required_subjects
    ''', (year,))
    
    subject_stats = cursor.fetchall()
    
    # 按校区统计
    cursor.execute('''
        SELECT campus, COUNT(*) as count, SUM(enrollment_count) as enrollment
        FROM yunnan_b_segment_plans 
        WHERE year = ?
        GROUP BY campus
    ''', (year,))
    
    campus_stats = cursor.fetchall()
    
    conn.close()
    
    return {
        "year": year,
        "总体统计": {
            "学校数量": stats['university_count'],
            "专业组数量": stats['total_majors'],
            "总招生人数": stats['total_enrollment'],
            "平均学费": round(stats['avg_tuition'], 2) if stats['avg_tuition'] else None
        },
        "选考科目分布": [{"科目": row['required_subjects'], "专业数": row['count'], "招生人数": row['enrollment']} for row in subject_stats],
        "校区分布": [{"校区": row['campus'], "专业数": row['count'], "招生人数": row['enrollment']} for row in campus_stats]
    }
