-- 云志选 - 招生分数线数据表设计
-- 创建时间: 2026-03-11
-- 用途: 存储各高校在各省的招生分数线数据

-- ============================================
-- 表1: 招生分数线主表 (admission_scores)
-- ============================================
CREATE TABLE IF NOT EXISTS admission_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 学校信息
    university_id TEXT NOT NULL,           -- 关联 universities.id (如: beida)
    university_name TEXT,                  -- 学校名称冗余存储(如: 北京大学)
    
    -- 招生年份和省份
    year INTEGER NOT NULL,                 -- 招生年份: 2024, 2025
    province TEXT NOT NULL,                -- 招生省份: 云南、四川等
    
    -- 科类信息
    subject_type TEXT NOT NULL,            -- 科类: 物理类/历史类(新高考) 或 理科/文科(老高考)
    
    -- 批次信息
    admission_batch TEXT,                  -- 招生批次: 一本、二本、提前批等
    
    -- 专业信息
    major_category TEXT,                   -- 专业大类: 数学类、物理学类等
    major_name TEXT,                       -- 具体专业名称(可选)
    
    -- 招生人数
    enrollment_count INTEGER,              -- 招生人数
    
    -- 分数数据
    max_score INTEGER,                     -- 最高分
    min_score INTEGER,                     -- 最低分
    avg_score INTEGER,                     -- 平均分(可选)
    
    -- 位次数据(如果有)
    max_rank INTEGER,                      -- 最高位次
    min_rank INTEGER,                      -- 最低位次
    
    -- 备注
    notes TEXT,                            -- 备注信息
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source TEXT,                      -- 数据来源: 官方/用户录入/网络采集
    
    -- 索引
    FOREIGN KEY (university_id) REFERENCES universities(id),
    UNIQUE(year, province, subject_type, university_id, major_category)  -- 防止重复数据
);

-- 创建索引以提高查询效率
CREATE INDEX IF NOT EXISTS idx_admission_year ON admission_scores(year);
CREATE INDEX IF NOT EXISTS idx_admission_province ON admission_scores(province);
CREATE INDEX IF NOT EXISTS idx_admission_university ON admission_scores(university_id);
CREATE INDEX IF NOT EXISTS idx_admission_subject ON admission_scores(subject_type);
CREATE INDEX IF NOT EXISTS idx_admission_score ON admission_scores(min_score);

-- ============================================
-- 表2: 省份科类对照表 (province_subjects)
-- ============================================
-- 用于管理不同省份的科类命名(新高考vs老高考)
CREATE TABLE IF NOT EXISTS province_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    province TEXT NOT NULL,                -- 省份名称
    year INTEGER NOT NULL,                 -- 年份
    subject_type TEXT NOT NULL,            -- 科类: 物理类/历史类/理科/文科
    subject_type_alias TEXT,               -- 别名: 理工/文史等
    is_new_gaokao BOOLEAN,                 -- 是否新高考: 1=是, 0=否
    subjects_required TEXT,                -- 选科要求JSON: ["物理","化学"]
    total_score INTEGER DEFAULT 750,       -- 总分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(province, year, subject_type)
);

-- ============================================
-- 表3: 数据导入日志表 (import_logs)
-- ============================================
-- 用于追踪数据导入历史
CREATE TABLE IF NOT EXISTS import_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_name TEXT,                        -- 导入文件名
    data_type TEXT,                        -- 数据类型: 分数线/位次等
    year INTEGER,                          -- 数据年份
    province TEXT,                         -- 数据省份
    record_count INTEGER,                  -- 导入记录数
    success_count INTEGER,                 -- 成功数
    error_count INTEGER,                   -- 失败数
    error_details TEXT,                    -- 错误详情
    imported_by TEXT                       -- 导入者
);

-- ============================================
-- 插入示例数据: 北京大学2024年云南招生数据
-- ============================================

-- 先确保北京大学在 universities 表中
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
INSERT INTO admission_scores (
    university_id, university_name, year, province, subject_type, 
    admission_batch, major_category, enrollment_count,
    max_score, min_score, notes, data_source
) VALUES 
('beida', '北京大学', 2024, '云南', '物理类', '一本', '数学类', 1, 719, 719, NULL, '用户录入'),
('beida', '北京大学', 2024, '云南', '物理类', '一本', '物理学类', 1, 703, 703, NULL, '用户录入'),
('beida', '北京大学', 2024, '云南', '物理类', '一本', '电子信息类', 1, 698, 698, NULL, '用户录入'),
('beida', '北京大学', 2024, '云南', '物理类', '一本', '计算机类', 2, 707, 698, NULL, '用户录入'),
('beida', '北京大学', 2024, '云南', '物理类', '一本', '化学类', 1, 699, 699, NULL, '用户录入'),
('beida', '北京大学', 2024, '云南', '物理类', '一本', '生物科学类', 2, 699, 697, NULL, '用户录入'),
('beida', '北京大学', 2024, '云南', '物理类', '一本', '理科试验班类(元培)', 1, 731, 731, NULL, '用户录入');

-- 插入省份科类对照数据
INSERT OR IGNORE INTO province_subjects (province, year, subject_type, subject_type_alias, is_new_gaokao, subjects_required)
VALUES 
('云南', 2024, '物理类', '理工', 1, '["物理"]'),
('云南', 2024, '历史类', '文史', 1, '["历史"]'),
('云南', 2025, '物理类', '理工', 1, '["物理"]'),
('云南', 2025, '历史类', '文史', 1, '["历史"]');
