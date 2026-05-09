from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from db import get_db_path, get_connection

# 导入云南物理类招生数据 API
from yunnan_physics_api import router as yunnan_physics_router
from yunnan_score_segments_api import router as yunnan_segments_router
from yunnan_plan_api import router as yunnan_b_segment_router
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
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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
    year: Optional[int] = None    # 参考年份，默认取最新

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
    min_rank: Optional[int] = None  # 最低位次
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

    # 招生计划表（统一本科批各段）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS yunnan_plan_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        university_id TEXT NOT NULL,
        university_name TEXT NOT NULL,
        major_group_sequence TEXT,
        major_code TEXT NOT NULL,
        major_group_name TEXT,
        required_subjects TEXT,
        major_category TEXT NOT NULL,
        included_majors TEXT,
        tuition INTEGER,
        enrollment_count INTEGER,
        campus TEXT,
        notes TEXT,
        batch_type TEXT NOT NULL DEFAULT '本科批B段',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source TEXT,
        UNIQUE(year, university_id, major_code, major_category, batch_type)
    )
    ''')

    # 迁移：旧表 → 新表
    try:
        old_exists = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yunnan_b_segment_plans'").fetchone()
        if old_exists:
            new_exists = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yunnan_plan_data'").fetchone()
            if not new_exists:
                cursor.execute("ALTER TABLE yunnan_b_segment_plans RENAME TO yunnan_plan_data")
                cursor.execute("ALTER TABLE yunnan_plan_data ADD COLUMN batch_type TEXT NOT NULL DEFAULT '本科批B段'")
            else:
                # 新表已存在，确保旧数据已迁入后删除旧表
                cursor.execute("INSERT OR IGNORE INTO yunnan_plan_data (id, year, university_id, university_name, major_group_sequence, major_code, major_group_name, required_subjects, major_category, included_majors, tuition, enrollment_count, campus, notes, batch_type, created_at, updated_at, data_source) SELECT id, year, university_id, university_name, major_group_sequence, major_code, major_group_name, required_subjects, major_category, included_majors, tuition, enrollment_count, campus, notes, '本科批B段', created_at, updated_at, data_source FROM yunnan_b_segment_plans")
                cursor.execute("DROP TABLE yunnan_b_segment_plans")
            conn.commit()
    except Exception:
        pass

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
async def score_to_rank(score: int, year: Optional[int] = None):
    """分数转位次（基于数据库一分一段表，默认取最新年份）"""
    rank, year_used = convert_score_to_rank(score, year)
    return {"score": score, "estimated_rank": rank, "year_used": year_used}

def convert_score_to_rank(score: int, year: Optional[int] = None) -> tuple:
    """
    分数转位次（基于数据库一分一段表）
    使用线性插值估算，返回 (rank, year_used)
    """
    conn = get_connection()
    cursor = conn.cursor()

    if year is None:
        cursor.execute("SELECT MAX(year) FROM yunnan_physics_score_segments")
        row = cursor.fetchone()
        year = row[0] if row else 2025

    # 精确匹配
    cursor.execute(
        "SELECT cumulative_count FROM yunnan_physics_score_segments WHERE year=? AND score=?",
        (year, score))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row['cumulative_count'], year

    # 插值：找 score 两侧最近的两条记录
    cursor.execute(
        "SELECT score, cumulative_count FROM yunnan_physics_score_segments WHERE year=? AND score < ? ORDER BY score DESC LIMIT 1",
        (year, score))
    lower = cursor.fetchone()

    cursor.execute(
        "SELECT score, cumulative_count FROM yunnan_physics_score_segments WHERE year=? AND score > ? ORDER BY score ASC LIMIT 1",
        (year, score))
    higher = cursor.fetchone()

    conn.close()

    if lower and higher:
        x1, y1 = lower['score'], lower['cumulative_count']
        x2, y2 = higher['score'], higher['cumulative_count']
        rank = int(y1 + (y2 - y1) * (score - x1) / (x2 - x1))
        return rank, year

    if lower:
        return lower['cumulative_count'], year
    if higher:
        return higher['cumulative_count'], year
    return 5000, year

def calculate_recommendations(student: StudentInfo) -> List[RecommendationResult]:
    score = student.score
    rank = student.rank
    risk = student.risk_tolerance

    if not rank:
        rank, _ = convert_score_to_rank(score)

    # 确定查询年份
    year = student.year
    if year is None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(year) FROM yunnan_physics_scores")
        row = cursor.fetchone()
        year = row[0] if row else 2024
        conn.close()

    # 位次容差范围（位次越小=排名越高）
    # 冲：院校位次高于考生（位次数字更小），稳：院校位次接近考生，保：院校位次低于考生
    RANK_TOLERANCE = {
        "激进": {"冲": (rank - 500, rank), "稳": (rank - 500, rank + 500), "保": (rank + 500, rank + 1500)},
        "稳健": {"冲": (rank - 300, rank), "稳": (rank - 300, rank + 300), "保": (rank + 300, rank + 1000)},
        "保守": {"冲": (rank - 200, rank), "稳": (rank - 200, rank + 200), "保": (rank + 200, rank + 800)},
    }

    tiers = RANK_TOLERANCE.get(risk, RANK_TOLERANCE["稳健"])
    chong_rank_min, chong_rank_max = tiers["冲"]
    wen_rank_min, wen_rank_max = tiers["稳"]
    bao_rank_min, bao_rank_max = tiers["保"]

    # 查询数据库
    conn = get_connection()
    cursor = conn.cursor()

    # 冲：院校位次高于考生（min_rank更小）
    cursor.execute('''
    SELECT s.*, u.level, u.province
    FROM yunnan_physics_scores s
    JOIN universities u ON s.university_id = u.id
    WHERE s.year = ? AND s.min_rank >= ? AND s.min_rank <= ?
    ORDER BY s.min_rank ASC, s.enrollment_count DESC
    LIMIT 20
    ''', (year, chong_rank_min, chong_rank_max))
    chong_majors = cursor.fetchall()

    # 稳：院校位次接近考生
    cursor.execute('''
    SELECT s.*, u.level, u.province
    FROM yunnan_physics_scores s
    JOIN universities u ON s.university_id = u.id
    WHERE s.year = ? AND s.min_rank >= ? AND s.min_rank <= ?
    ORDER BY ABS(s.min_rank - ?) ASC, s.enrollment_count DESC
    LIMIT 30
    ''', (year, wen_rank_min, wen_rank_max, rank))
    wen_majors = cursor.fetchall()

    # 保：院校位次低于考生（min_rank更大）
    cursor.execute('''
    SELECT s.*, u.level, u.province
    FROM yunnan_physics_scores s
    JOIN universities u ON s.university_id = u.id
    WHERE s.year = ? AND s.min_rank >= ? AND s.min_rank <= ?
    ORDER BY s.min_rank DESC, s.enrollment_count DESC
    LIMIT 20
    ''', (year, bao_rank_min, bao_rank_max))
    bao_majors = cursor.fetchall()

    conn.close()

    # 生成推荐结果
    recommendations = []
    order = 1

    # 冲刺层（4个）
    for row in chong_majors[:4]:
        major = dict(row)
        rank_diff = rank - major['min_rank']  # 正值=考生位次更高(数字更小)
        prob = max(15, min(45, 45 - abs(rank_diff) / 10))
        recommendations.append({
            "level": "冲",
            "university_name": major['university_name'],
            "university_id": major['university_id'],
            "major": major['major_category'],
            "major_code": major.get('major_code', ''),
            "min_score": major['min_score'],
            "min_rank": major.get('min_rank'),
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
        rank_diff = abs(rank - major['min_rank'])
        prob = max(50, min(85, 85 - rank_diff / 10))
        recommendations.append({
            "level": "稳",
            "university_name": major['university_name'],
            "university_id": major['university_id'],
            "major": major['major_category'],
            "major_code": major.get('major_code', ''),
            "min_score": major['min_score'],
            "min_rank": major.get('min_rank'),
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
        rank_diff = major['min_rank'] - rank  # 正值=院校位次更低(数字更大)
        prob = max(90, min(98, 90 + rank_diff / 20))
        recommendations.append({
            "level": "保",
            "university_name": major['university_name'],
            "university_id": major['university_id'],
            "major": major['major_category'],
            "major_code": major.get('major_code', ''),
            "min_score": major['min_score'],
            "min_rank": major.get('min_rank'),
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
