-- 云志选 - 云南省物理类招生分数线数据表
-- 创建时间: 2026-03-11
-- 适用范围: 云南省 + 物理类（新高考）

-- ============================================
-- 招生分数线表 (yunnan_physics_scores)
-- ============================================
CREATE TABLE IF NOT EXISTS yunnan_physics_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 学校信息（与 universities 表关联）
    university_id TEXT NOT NULL,           -- 如: beida, tsinghua
    university_name TEXT NOT NULL,         -- 学校名称（冗余，方便查询）
    
    -- 招生年份
    year INTEGER NOT NULL,                 -- 2024, 2025
    
    -- 专业信息
    major_category TEXT NOT NULL,          -- 专业大类：数学类、物理学类、计算机类等
    major_code TEXT,                       -- 专业代码（可选）
    
    -- 招生人数
    enrollment_count INTEGER,              -- 招生人数
    
    -- 分数数据
    max_score INTEGER,                     -- 最高分
    min_score INTEGER NOT NULL,            -- 最低分（必填，用于志愿推荐）
    avg_score INTEGER,                     -- 平均分
    
    -- 位次数据（用于精准推荐）
    min_rank INTEGER,                      -- 最低位次（重要！用于匹配考生位次）
    
    -- 备注
    notes TEXT,                            -- 特殊说明
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 防止重复数据（同一年同一学校同一专业）
    UNIQUE(year, university_id, major_category)
);

-- 创建常用查询索引
CREATE INDEX IF NOT EXISTS idx_yunnan_year ON yunnan_physics_scores(year);
CREATE INDEX IF NOT EXISTS idx_yunnan_university ON yunnan_physics_scores(university_id);
CREATE INDEX IF NOT EXISTS idx_yunnan_score ON yunnan_physics_scores(min_score);
CREATE INDEX IF NOT EXISTS idx_yunnan_rank ON yunnan_physics_scores(min_rank);

-- ============================================
-- 插入北京大学2024年云南物理类招生数据
-- ============================================

-- 确保北京大学在 universities 表中
INSERT OR IGNORE INTO universities (id, name, province, city, level, admission_mode, website, min_score_2025, min_rank_2025, subjects_required, majors, advantages, disadvantages)
VALUES (
    'beida',
    '北京大学',
    '北京',
    '北京',
    '985',
    '统招/强基计划',
    'https://www.pku.edu.cn/',
    NULL,
    NULL,
    '["物理","化学"]',
    '[{"name":"数学类","code":"0701"},{"name":"物理学类","code":"0702"},{"name":"电子信息类","code":"0807"},{"name":"计算机类","code":"0809"},{"name":"化学类","code":"0703"},{"name":"生物科学类","code":"0710"},{"name":"理科试验班类(元培)","code":"0700"}]',
    '["国内顶尖学府","文理并重","元培学院通识教育","强大校友网络"]',
    '["竞争激烈","录取分数极高","学业压力大"]'
);

-- 插入招生分数线数据
INSERT OR REPLACE INTO yunnan_physics_scores (
    university_id, university_name, year, major_category, major_code,
    enrollment_count, max_score, min_score, avg_score, min_rank, notes
) VALUES 
('beida', '北京大学', 2024, '数学类', '0701', 1, 719, 719, 719, NULL, '最高分专业'),
('beida', '北京大学', 2024, '物理学类', '0702', 1, 703, 703, 703, NULL, NULL),
('beida', '北京大学', 2024, '电子信息类', '0807', 1, 698, 698, 698, NULL, NULL),
('beida', '北京大学', 2024, '计算机类', '0809', 2, 707, 698, 702, NULL, '招2人'),
('beida', '北京大学', 2024, '化学类', '0703', 1, 699, 699, 699, NULL, NULL),
('beida', '北京大学', 2024, '生物科学类', '0710', 2, 699, 697, 698, NULL, '招2人'),
('beida', '北京大学', 2024, '理科试验班类(元培)', '0700', 1, 731, 731, 731, NULL, '最高分731');
