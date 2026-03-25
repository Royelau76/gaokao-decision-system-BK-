#!/usr/bin/env python3
"""
院校数据导入脚本
将JSON数据导入SQLite数据库
"""

import sqlite3
import json
import os

def init_database():
    """初始化数据库表结构"""
    # 确保data目录存在
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    db_path = os.path.join(data_dir, 'gaokao.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 删除旧表（如果存在）
    cursor.execute('DROP TABLE IF EXISTS universities')
    
    # 创建院校表
    cursor.execute('''
    CREATE TABLE universities (
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
    
    conn.commit()
    conn.close()
    print("✅ 数据库表创建成功")

def import_universities():
    """导入院校数据"""
    # 读取JSON文件
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    json_path = os.path.join(data_dir, 'universities.json')
    db_path = os.path.join(data_dir, 'gaokao.db')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        universities = json.load(f)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 插入数据
    for uni in universities:
        cursor.execute('''
        INSERT INTO universities (
            id, name, province, city, level, admission_mode, website,
            min_score_2025, min_rank_2025, subjects_required, majors,
            advantages, disadvantages
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            uni['id'],
            uni['name'],
            uni.get('province', ''),
            uni.get('city', ''),
            uni.get('level', ''),
            uni.get('admission_mode', ''),
            uni.get('website', ''),
            uni.get('min_score_2025', 0),
            uni.get('min_rank_2025', 0),
            json.dumps(uni.get('subjects_required', []), ensure_ascii=False),
            json.dumps(uni.get('majors', []), ensure_ascii=False),
            json.dumps(uni.get('advantages', []), ensure_ascii=False),
            json.dumps(uni.get('disadvantages', []), ensure_ascii=False)
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 成功导入 {len(universities)} 所院校数据")

def verify_data():
    """验证数据导入"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    db_path = os.path.join(data_dir, 'gaokao.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM universities ORDER BY min_rank_2025')
    rows = cursor.fetchall()
    
    print("\n📊 院校数据概览：\n")
    print(f"{'院校':<20} {'层次':<8} {'招生方式':<12} {'2025最低分':<10} {'位次':<8}")
    print("-" * 65)
    
    for row in rows:
        print(f"{row['name']:<18} {row['level']:<8} {row['admission_mode']:<12} "
              f"{row['min_score_2025']:<10} {row['min_rank_2025']:<8}")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 开始初始化院校数据库...\n")
    
    print("1️⃣ 创建数据库表...")
    init_database()
    
    print("\n2️⃣ 导入院校数据...")
    import_universities()
    
    print("\n3️⃣ 验证数据...")
    verify_data()
    
    print("\n✨ 数据库初始化完成！")
