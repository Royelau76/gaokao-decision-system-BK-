from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import os
from datetime import datetime

from db import get_db_path, get_connection

# 导入云南物理类招生数据 API
from yunnan_physics_api import router as yunnan_physics_router
from yunnan_score_segments_api import router as yunnan_segments_router
from yunnan_b_segment_api import router as yunnan_b_segment_router
from query_api import router as query_router
from data_entry_api import router as data_entry_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="云志选 - 云南高考志愿决策系统",
    description="2026年云南省高考志愿填报智能决策支持系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册云南物理类招生数据路由
app.include_router(yunnan_physics_router)
app.include_router(yunnan_segments_router)
app.include_router(yunnan_b_segment_router)
app.include_router(query_router)
app.include_router(data_entry_router)

# 数据模型
class StudentInfo(BaseModel):
    """考生信息"""
    score: int                    # 高考总分
    rank: int                     # 全省位次
    subjects: List[str]           # 选科组合
    preference_region: List[str]  # 偏好地区
    preference_major: List[str]   # 偏好专业
    risk_tolerance: str           # 风险偏好：激进/稳健/保守

class University(BaseModel):
    """院校信息"""
    id: str
    name: str
    province: str
    level: str                    # 985/211/双一流/普通
    admission_mode: str           # 统招/综合评价/强基计划
    min_score_2025: int          # 2025年最低分
    min_rank_2025: int           # 2025年最低位次
    majors: List[dict]           # 专业列表

class RecommendationResult(BaseModel):
    """推荐结果"""
    level: str                    # 冲/稳/保
    university_name: str          # 院校名称
    university_id: str            # 院校ID
    major: str                    # 专业
    major_code: str = ""          # 专业代码
    min_score: float = 0          # 最低分
    max_score: Optional[float] = None
    avg_score: Optional[float] = None
    enrollment_count: Optional[int] = None
    admission_probability: float  # 录取概率
    suggested_order: int          # 建议排序
    school_level: str = ""        # 院校层次

class VolunteerPlan(BaseModel):
    """志愿方案"""
    id: str
    name: str
    student_info: StudentInfo
    recommendations: List[RecommendationResult]
    created_at: datetime

def init_database():
    """初始化SQLite数据库 - 创建所有需要的表"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # 院校表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS universities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        province TEXT,
        city TEXT,
        level TEXT,
        admission_mode TEXT,
        website TEXT,
        min_score_2025 INTEGER,
        min_rank_2025 INTEGER,
        subjects_required TEXT,
        majors TEXT,
        advantages TEXT,
        disadvantages TEXT
    )
    ''')

    # 考生信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        score INTEGER,
        rank INTEGER,
        subjects TEXT,
        preference_region TEXT,
        preference_major TEXT,
        risk_tolerance TEXT
    )
    ''')

    # 志愿方案表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS volunteer_plans (
        id TEXT PRIMARY KEY,
        name TEXT,
        student_id TEXT,
        recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 云南物理类招生分数线表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS yunnan_physics_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        university_id TEXT NOT NULL,
        university_name TEXT NOT NULL,
        year INTEGER NOT NULL,
        major_category TEXT NOT NULL,
        major_code TEXT,
        enrollment_count INTEGER,
        max_score INTEGER,
        min_score INTEGER NOT NULL,
        avg_score INTEGER,
        min_rank INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(year, university_id, major_category)
    )
    ''')

    # 一分一段表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS yunnan_physics_score_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        score INTEGER NOT NULL,
        count INTEGER NOT NULL,
        cumulative_count INTEGER NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source TEXT,
        UNIQUE(year, score)
    )
    ''')

    # 本科批B段招生计划表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS yunnan_b_segment_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        university_id TEXT NOT NULL,
        university_name TEXT NOT NULL,
        major_group_code TEXT NOT NULL,
        major_group_name TEXT,
        required_subjects TEXT,
        major_category TEXT NOT NULL,
        included_majors TEXT,
        tuition INTEGER,
        enrollment_count INTEGER,
        campus TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source TEXT,
        UNIQUE(year, university_id, major_group_code, major_category)
    )
    ''')

    # 招生分数线主表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admission_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        university_id TEXT NOT NULL,
        university_name TEXT,
        year INTEGER NOT NULL,
        province TEXT NOT NULL,
        subject_type TEXT NOT NULL,
        admission_batch TEXT,
        major_category TEXT,
        major_name TEXT,
        enrollment_count INTEGER,
        max_score INTEGER,
        min_score INTEGER,
        avg_score INTEGER,
        max_rank INTEGER,
        min_rank INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source TEXT,
        UNIQUE(year, province, subject_type, university_id, major_category)
    )
    ''')

    conn.commit()
    conn.close()

@app.get("/")
async def root():
    return {"message": "云志选系统API", "version": "1.0.0"}

@app.get("/api/universities")
async def get_universities(
    province: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取院校列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM universities WHERE 1=1"
    params = []
    
    if province:
        query += " AND province = ?"
        params.append(province)
    if level:
        query += " AND level = ?"
        params.append(level)
    
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    universities = []
    for row in rows:
        uni = dict(row)
        uni['majors'] = json.loads(uni['majors']) if uni['majors'] else []
        universities.append(uni)
    
    conn.close()
    return universities

@app.post("/api/recommendations")
async def get_recommendations(student: StudentInfo):
    """获取智能推荐"""
    # 调用推荐算法
    recommendations = calculate_recommendations(student)
    return {
        "status": "success",
        "student_info": {
            "score": student.score,
            "rank": student.rank,
            "risk_tolerance": student.risk_tolerance,
            "preference_major": student.preference_major
        },
        "recommendations": recommendations,
        "summary": {
            "冲": len([r for r in recommendations if r["level"] == "冲"]),
            "稳": len([r for r in recommendations if r["level"] == "稳"]),
            "保": len([r for r in recommendations if r["level"] == "保"])
        }
    }

@app.post("/api/volunteer-plans")
async def create_volunteer_plan(plan: VolunteerPlan):
    """创建志愿方案"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO volunteer_plans (id, name, student_id, recommendations)
    VALUES (?, ?, ?, ?)
    ''', (
        plan.id,
        plan.name,
        json.dumps(plan.student_info.model_dump()),
        json.dumps([r.model_dump() for r in plan.recommendations])
    ))
    
    conn.commit()
    conn.close()
    return {"status": "success", "message": "志愿方案已保存"}

@app.get("/api/score-conversion")
async def score_to_rank(score: int):
    """分数转位次（基于2025年一分一段表）"""
    rank = convert_score_to_rank(score)
    return {"score": score, "estimated_rank": rank}

def calculate_recommendations(student: StudentInfo) -> List[RecommendationResult]:
    """
    核心推荐算法
    基于2024年实际录取数据，推荐冲稳保三个梯度的院校专业
    """
    recommendations = []
    
    score = student.score
    rank = student.rank
    risk = student.risk_tolerance
    
    # 根据风险偏好调整分数范围
    if risk == "激进":
        chong_score_min = score + 3      # 冲：高3-10分
        chong_score_max = score + 10
        wen_score_min = score - 2        # 稳：±2分
        wen_score_max = score + 2
        bao_score_max = score - 3        # 保：低3-15分
        bao_score_min = score - 15
    elif risk == "保守":
        chong_score_min = score + 1      # 冲：高1-5分
        chong_score_max = score + 5
        wen_score_min = score - 5        # 稳：±5分
        wen_score_max = score + 5
        bao_score_max = score - 5        # 保：低5-20分
        bao_score_min = score - 20
    else:  # 稳健
        chong_score_min = score + 2      # 冲：高2-8分
        chong_score_max = score + 8
        wen_score_min = score - 3        # 稳：±3分
        wen_score_max = score + 3
        bao_score_max = score - 3        # 保：低3-15分
        bao_score_min = score - 15
    
    # 查询数据库
    conn = get_connection()
    cursor = conn.cursor()
    
    # 冲：分数略高于考生（按专业粒度）
    cursor.execute('''
    SELECT s.*, u.level, u.province 
    FROM yunnan_physics_scores s
    JOIN universities u ON s.university_id = u.id
    WHERE s.year = 2024 AND s.min_score >= ? AND s.min_score <= ?
    ORDER BY s.min_score ASC, s.enrollment_count DESC
    LIMIT 20
    ''', (chong_score_min, chong_score_max))
    chong_majors = cursor.fetchall()
    
    # 稳：分数匹配考生
    cursor.execute('''
    SELECT s.*, u.level, u.province 
    FROM yunnan_physics_scores s
    JOIN universities u ON s.university_id = u.id
    WHERE s.year = 2024 AND s.min_score >= ? AND s.min_score <= ?
    ORDER BY ABS(s.min_score - ?) ASC, s.enrollment_count DESC
    LIMIT 30
    ''', (wen_score_min, wen_score_max, score))
    wen_majors = cursor.fetchall()
    
    # 保：分数低于考生
    cursor.execute('''
    SELECT s.*, u.level, u.province 
    FROM yunnan_physics_scores s
    JOIN universities u ON s.university_id = u.id
    WHERE s.year = 2024 AND s.min_score >= ? AND s.min_score < ?
    ORDER BY s.min_score DESC, s.enrollment_count DESC
    LIMIT 20
    ''', (bao_score_min, bao_score_max))
    bao_majors = cursor.fetchall()
    
    conn.close()
    
    # 生成推荐结果
    order = 1
    
    # 冲刺层（4个）
    for row in chong_majors[:4]:
        major = dict(row)
        prob = max(15, 45 - (major['min_score'] - score) * 5)
        recommendations.append({
            "level": "冲",
            "university_name": major['university_name'],
            "university_id": major['university_id'],
            "major": major['major_category'],
            "major_code": major.get('major_code', ''),
            "min_score": major['min_score'],
            "max_score": major.get('max_score'),
            "avg_score": major.get('avg_score'),
            "enrollment_count": major.get('enrollment_count'),
            "admission_probability": round(prob, 1),
            "suggested_order": order,
            "school_level": major.get('level', '')
        })
        order += 1

    # 稳妥层（10个）
    for row in wen_majors[:10]:
        major = dict(row)
        score_diff = abs(major['min_score'] - score)
        prob = max(50, 85 - score_diff * 8)
        recommendations.append({
            "level": "稳",
            "university_name": major['university_name'],
            "university_id": major['university_id'],
            "major": major['major_category'],
            "major_code": major.get('major_code', ''),
            "min_score": major['min_score'],
            "max_score": major.get('max_score'),
            "avg_score": major.get('avg_score'),
            "enrollment_count": major.get('enrollment_count'),
            "admission_probability": round(prob, 1),
            "suggested_order": order,
            "school_level": major.get('level', '')
        })
        order += 1

    # 保底层（6个）
    for row in bao_majors[:6]:
        major = dict(row)
        prob = min(95, 90 + (score - major['min_score']) * 2)
        recommendations.append({
            "level": "保",
            "university_name": major['university_name'],
            "university_id": major['university_id'],
            "major": major['major_category'],
            "major_code": major.get('major_code', ''),
            "min_score": major['min_score'],
            "max_score": major.get('max_score'),
            "avg_score": major.get('avg_score'),
            "enrollment_count": major.get('enrollment_count'),
            "admission_probability": round(prob, 1),
            "suggested_order": order,
            "school_level": major.get('level', '')
        })
        order += 1
    
    return recommendations

def select_best_major(university: dict, student: StudentInfo) -> str:
    """根据考生偏好选择最佳专业"""
    majors = university.get('majors', [])

    # 如果majors是字符串，解析它
    if isinstance(majors, str):
        majors = json.loads(majors) if majors else []

    if not majors:
        return "专业待定"

    # 简单匹配：优先选择考生偏好专业
    for pref in student.preference_major:
        for major in majors:
            if pref in major.get('name', ''):
                return major['name']

    # 默认返回第一个专业
    return majors[0].get('name', '专业待定')

def convert_score_to_rank(score: int) -> int:
    """
    分数转位次（基于2025年云南一分一段表）
    使用线性插值估算
    """
    # 2025年云南物理类一分一段表关键点
    score_rank_map = {
        683: 52,
        675: 95,
        670: 169,
        665: 268,
        660: 415,
        655: 619,
        650: 876,
        645: 1261,
        640: 1698,
        635: 2260,
        630: 2974,
        625: 3813,
        620: 4699,
        615: 4901,
    }
    
    # 找到最近的两个点进行插值
    scores = sorted(score_rank_map.keys())
    
    if score >= max(scores):
        return score_rank_map[max(scores)]
    if score <= min(scores):
        return score_rank_map[min(scores)]
    
    for i in range(len(scores) - 1):
        if scores[i] <= score <= scores[i + 1]:
            # 线性插值
            x1, y1 = scores[i], score_rank_map[scores[i]]
            x2, y2 = scores[i + 1], score_rank_map[scores[i + 1]]
            rank = y1 + (y2 - y1) * (score - x1) / (x2 - x1)
            return int(rank)
    
    return 5000  # 默认值

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
