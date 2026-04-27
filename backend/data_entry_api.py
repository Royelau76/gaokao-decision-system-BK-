"""
数据录入 API - 录取分数线、一分一段、院校管理 CRUD
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from db import get_connection

router = APIRouter(prefix="/api/data-entry", tags=["数据录入"])


# =========== 录取分数线 ===========

class AdmissionScoreInput(BaseModel):
    university_id: str
    university_name: str
    year: int
    major_category: str
    major_code: Optional[str] = ""
    enrollment_count: Optional[int] = None
    max_score: Optional[float] = None
    min_score: float
    avg_score: Optional[float] = None
    min_rank: Optional[int] = None
    notes: Optional[str] = ""


@router.get("/scores")
async def list_scores(year: Optional[int] = None, university_id: Optional[str] = None,
                       limit: int = 500):
    conn = get_connection()
    c = conn.cursor()
    conds = ["1=1"]
    params = []
    if year: conds.append("year=?"); params.append(year)
    if university_id: conds.append("university_id=?"); params.append(university_id)
    c.execute(f"SELECT * FROM yunnan_physics_scores WHERE {' AND '.join(conds)} ORDER BY year DESC, min_score DESC LIMIT ?",
              params + [limit])
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


@router.post("/scores")
async def create_score(item: AdmissionScoreInput):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO yunnan_physics_scores
                (university_id, university_name, year, major_category, major_code,
                 enrollment_count, max_score, min_score, avg_score, min_rank, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (item.university_id, item.university_name, item.year, item.major_category,
              item.major_code or "", item.enrollment_count, item.max_score, item.min_score,
              item.avg_score, item.min_rank, item.notes or ""))
        conn.commit()
        return {"status": "ok", "id": c.lastrowid}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.put("/scores/{row_id}")
async def update_score(row_id: int, item: AdmissionScoreInput):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE yunnan_physics_scores SET
                university_id=?, university_name=?, year=?, major_category=?, major_code=?,
                enrollment_count=?, max_score=?, min_score=?, avg_score=?, min_rank=?, notes=?
            WHERE id=?
        """, (item.university_id, item.university_name, item.year, item.major_category,
              item.major_code or "", item.enrollment_count, item.max_score, item.min_score,
              item.avg_score, item.min_rank, item.notes or "", row_id))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.delete("/scores/{row_id}")
async def delete_score(row_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM yunnan_physics_scores WHERE id=?", (row_id,))
    conn.commit()
    conn.close()
    return {"status": "ok"}


# =========== 一分一段 ===========

class ScoreSegmentInput(BaseModel):
    year: int
    score: int
    count: int
    cumulative_count: int
    notes: Optional[str] = ""
    data_source: Optional[str] = ""


@router.get("/segments")
async def list_segments(year: Optional[int] = None, limit: int = 500):
    conn = get_connection()
    c = conn.cursor()
    if year:
        c.execute("SELECT * FROM yunnan_physics_score_segments WHERE year=? ORDER BY score DESC LIMIT ?", (year, limit))
    else:
        c.execute("SELECT * FROM yunnan_physics_score_segments ORDER BY year DESC, score DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


@router.post("/segments")
async def create_segment(item: ScoreSegmentInput):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO yunnan_physics_score_segments (year, score, count, cumulative_count, notes, data_source)
            VALUES (?,?,?,?,?,?)
        """, (item.year, item.score, item.count, item.cumulative_count, item.notes or "", item.data_source or ""))
        conn.commit()
        return {"status": "ok", "id": c.lastrowid}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.put("/segments/{row_id}")
async def update_segment(row_id: int, item: ScoreSegmentInput):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE yunnan_physics_score_segments SET
                year=?, score=?, count=?, cumulative_count=?, notes=?, data_source=?
            WHERE id=?
        """, (item.year, item.score, item.count, item.cumulative_count, item.notes or "", item.data_source or "", row_id))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.delete("/segments/{row_id}")
async def delete_segment(row_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM yunnan_physics_score_segments WHERE id=?", (row_id,))
    conn.commit()
    conn.close()
    return {"status": "ok"}


# =========== 院校管理 ===========

class UniversityInput(BaseModel):
    id: str
    name: str
    province: Optional[str] = ""
    city: Optional[str] = ""
    level: Optional[str] = ""
    admission_mode: Optional[str] = ""
    website: Optional[str] = ""


@router.get("/universities-list")
async def list_all_universities():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, province, city, level, admission_mode, website FROM universities ORDER BY level, name")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


@router.post("/universities")
async def create_university(item: UniversityInput):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO universities (id, name, province, city, level, admission_mode, website)
            VALUES (?,?,?,?,?,?,?)
        """, (item.id, item.name, item.province or "", item.city or "", item.level or "",
              item.admission_mode or "", item.website or ""))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.put("/universities/{uni_id}")
async def update_university(uni_id: str, item: UniversityInput):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE universities SET name=?, province=?, city=?, level=?, admission_mode=?, website=?
            WHERE id=?
        """, (item.name, item.province or "", item.city or "", item.level or "",
              item.admission_mode or "", item.website or "", uni_id))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.delete("/universities/{uni_id}")
async def delete_university(uni_id: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM universities WHERE id=?", (uni_id,))
    conn.commit()
    conn.close()
    return {"status": "ok"}


# =========== 招生计划 ===========

class BSegmentPlanInput(BaseModel):
    university_id: str
    university_name: str
    year: int
    major_code: str
    major_group_sequence: Optional[str] = ""
    major_group_name: Optional[str] = ""
    required_subjects: Optional[str] = ""
    major_category: str
    included_majors: Optional[str] = ""
    tuition: Optional[int] = None
    enrollment_count: Optional[int] = None
    campus: Optional[str] = ""
    notes: Optional[str] = ""
    data_source: Optional[str] = ""


@router.get("/plans")
async def list_plans(year: Optional[int] = None, university_id: Optional[str] = None,
                      limit: int = 500):
    conn = get_connection()
    c = conn.cursor()
    conds = ["1=1"]
    params = []
    if year: conds.append("year=?"); params.append(year)
    if university_id: conds.append("university_id=?"); params.append(university_id)
    c.execute(f"SELECT * FROM yunnan_b_segment_plans WHERE {' AND '.join(conds)} ORDER BY year DESC, university_name, major_code LIMIT ?",
              params + [limit])
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


@router.post("/plans")
async def create_plan(item: BSegmentPlanInput):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO yunnan_b_segment_plans
                (university_id, university_name, year, major_code, major_group_sequence,
                 major_group_name, required_subjects, major_category, included_majors,
                 tuition, enrollment_count, campus, notes, data_source)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (item.university_id, item.university_name, item.year, item.major_code,
              item.major_group_sequence or "", item.major_group_name or "",
              item.required_subjects or "", item.major_category,
              item.included_majors or "", item.tuition, item.enrollment_count,
              item.campus or "", item.notes or "", item.data_source or ""))
        conn.commit()
        return {"status": "ok", "id": c.lastrowid}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.put("/plans/{row_id}")
async def update_plan(row_id: int, item: BSegmentPlanInput):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE yunnan_b_segment_plans SET
                university_id=?, university_name=?, year=?, major_code=?,
                major_group_sequence=?, major_group_name=?, required_subjects=?,
                major_category=?, included_majors=?, tuition=?, enrollment_count=?,
                campus=?, notes=?, data_source=?
            WHERE id=?
        """, (item.university_id, item.university_name, item.year, item.major_code,
              item.major_group_sequence or "", item.major_group_name or "",
              item.required_subjects or "", item.major_category,
              item.included_majors or "", item.tuition, item.enrollment_count,
              item.campus or "", item.notes or "", item.data_source or "", row_id))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.delete("/plans/{row_id}")
async def delete_plan(row_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM yunnan_b_segment_plans WHERE id=?", (row_id,))
    conn.commit()
    conn.close()
    return {"status": "ok"}


# =========== 批量 CSV 导入 ===========

class BatchImportRequest(BaseModel):
    table: str  # "scores" or "segments" or "plans"
    rows: List[dict]
    year: int


@router.post("/batch-import")
async def batch_import(req: BatchImportRequest):
    conn = get_connection()
    c = conn.cursor()
    ok = 0
    fail = 0
    errors = []

    for i, row in enumerate(req.rows):
        try:
            if req.table == "scores":
                c.execute("""
                    INSERT OR REPLACE INTO yunnan_physics_scores
                        (university_id, university_name, year, major_category, major_code,
                         enrollment_count, max_score, min_score, avg_score, min_rank, notes)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (row.get("university_id", ""), row.get("university_name", ""), req.year,
                      row.get("major_category", ""), row.get("major_code", ""),
                      row.get("enrollment_count"), row.get("max_score"), row.get("min_score"),
                      row.get("avg_score"), row.get("min_rank"), row.get("notes", "")))
            elif req.table == "segments":
                c.execute("""
                    INSERT OR REPLACE INTO yunnan_physics_score_segments (year, score, count, cumulative_count, notes)
                    VALUES (?,?,?,?,?)
                """, (req.year, row["score"], row["count"], row["cumulative_count"],
                      row.get("notes", "")))
            elif req.table == "plans":
                c.execute("""
                    INSERT OR REPLACE INTO yunnan_b_segment_plans
                        (university_id, university_name, year, major_code, major_group_sequence,
                         major_group_name, required_subjects, major_category, included_majors,
                         tuition, enrollment_count, campus, notes, data_source)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (row.get("university_id", ""), row.get("university_name", ""), req.year,
                      row.get("major_code", ""), row.get("major_group_sequence", ""),
                      row.get("major_group_name", ""), row.get("required_subjects", ""),
                      row.get("major_category", ""), row.get("included_majors", ""),
                      row.get("tuition"), row.get("enrollment_count"),
                      row.get("campus", ""), row.get("notes", ""), row.get("data_source", "")))
            ok += 1
        except Exception as e:
            fail += 1
            errors.append({"row": i, "error": str(e)})

    conn.commit()
    conn.close()
    return {"ok": ok, "fail": fail, "errors": errors[:10]}
