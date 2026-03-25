-- 云志选 - 云南省高考物理类本科批B段招生计划表
-- 创建时间: 2026-03-12
-- 适用范围: 云南省 + 物理类 + 本科批B段 + 2025-2026年

-- ============================================
-- 本科批B段招生计划表 (yunnan_b_segment_plans)
-- ============================================
CREATE TABLE IF NOT EXISTS yunnan_b_segment_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 年份
    year INTEGER NOT NULL,                 -- 2025, 2026
    
    -- 学校信息
    university_id TEXT NOT NULL,           -- 学校标识：beida, tsinghua等
    university_name TEXT NOT NULL,         -- 学校名称：北京大学
    
    -- 专业组信息
    major_group_code TEXT NOT NULL,        -- 专业组代码：01, 02, 04等
    major_group_name TEXT,                 -- 专业组名称
    
    -- 选考科目要求
    required_subjects TEXT,                -- 选考科目：化学、物理+化学等
    
    -- 专业信息
    major_category TEXT NOT NULL,          -- 专业大类：数学类、工科试验班类等
    included_majors TEXT,                  -- 包含专业详情（JSON格式或文本）
    
    -- 招生信息
    tuition INTEGER,                       -- 学费（元/年）
    enrollment_count INTEGER,              -- 招生人数
    
    -- 培养校区
    campus TEXT,                           -- 培养校区：校本部、深圳校区等
    
    -- 备注
    notes TEXT,                            -- 特殊说明
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source TEXT,                      -- 数据来源
    
    -- 防止重复数据（同一年同一学校同一专业组）
    UNIQUE(year, university_id, major_group_code, major_category)
);

-- 创建常用查询索引
CREATE INDEX IF NOT EXISTS idx_b_segment_year ON yunnan_b_segment_plans(year);
CREATE INDEX IF NOT EXISTS idx_b_segment_university ON yunnan_b_segment_plans(university_id);
CREATE INDEX IF NOT EXISTS idx_b_segment_major_group ON yunnan_b_segment_plans(major_group_code);
CREATE INDEX IF NOT EXISTS idx_b_segment_subjects ON yunnan_b_segment_plans(required_subjects);

-- ============================================
-- 插入北京大学2025年本科批B段招生计划
-- ============================================

INSERT OR REPLACE INTO yunnan_b_segment_plans (
    year, university_id, university_name, major_group_code, major_group_name,
    required_subjects, major_category, included_majors, tuition, enrollment_count, campus, data_source
) VALUES 
(2025, 'beida', '北京大学', '01', NULL, '化学', '数学类', 
 '["数学与应用数学(数学)", "数学与应用数学(概率统计)", "数学与应用数学(科学与工程计算)", "数学与应用数学(信息科学)", "数学与应用数学(金融)"]', 
 5000, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '02', NULL, '化学', '工科试验班类', 
 '["理论与应用力学、工程力学、能源与环境系统工程、航空航天工程、生物医学工程、材料科学与工程"]', 
 5000, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '04', NULL, '化学', '物理学类', 
 '["物理学、大气科学(大气与海洋)"]', 
 5000, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '05', NULL, '化学', '电子信息类', 
 '["电子信息科学与技术、微电子科学与工程"]', 
 5300, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '06', NULL, '化学', '计算机类', 
 '["计算机科学与技术、智能科学与技术"]', 
 5300, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '07', NULL, '化学', '化学类', 
 '["化学、应用化学、应用化学(材料方向)、化学生物学"]', 
 5000, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '08', NULL, '化学', '生物科学类', 
 '["生物科学、生物技术"]', 
 5300, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '09', NULL, '化学', '地球物理学类', 
 '["地球物理学、地理信息科学(遥感与地理信息系统)、空间科学与技术"]', 
 5000, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '11', NULL, '化学', '环境科学', 
 '["环境、健康、生态、地理与资源环境"]', 
 5000, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '16', NULL, '化学', '信息管理与信息系统', 
 '["信息管理与信息系统"]', 
 5000, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '18', NULL, '化学', '理科试验班类(元培)', 
 '["数学类、物理学类、地球物理学类、计算机类、电子信息类"]', 
 5300, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '20', NULL, '化学', '理科试验班类(经济)', 
 '["数学类"]', 
 5000, 1, '校本部', '官方发布'),

(2025, 'beida', '北京大学', '21', NULL, '化学', '理科试验班类(光华)', 
 '["数学类"]', 
 5000, 1, '校本部', '官方发布');
