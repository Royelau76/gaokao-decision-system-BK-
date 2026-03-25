-- 云志选 - 云南省物理类一分一段数据表
-- 创建时间: 2026-03-12
-- 适用范围: 云南省 + 物理类 + 2024-2026年

-- ============================================
-- 一分一段表 (yunnan_physics_score_segments)
-- ============================================
CREATE TABLE IF NOT EXISTS yunnan_physics_score_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 年份
    year INTEGER NOT NULL,                 -- 2024, 2025, 2026
    
    -- 分数信息
    score INTEGER NOT NULL,                -- 高考分数
    
    -- 人数统计
    count INTEGER NOT NULL,                -- 该分数同分人数
    cumulative_count INTEGER NOT NULL,     -- 累计人数（位次）
    
    -- 备注
    notes TEXT,                            -- 特殊说明
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source TEXT,                      -- 数据来源
    
    -- 防止重复数据（同一年同一分数）
    UNIQUE(year, score)
);

-- 创建常用查询索引
CREATE INDEX IF NOT EXISTS idx_segment_year ON yunnan_physics_score_segments(year);
CREATE INDEX IF NOT EXISTS idx_segment_score ON yunnan_physics_score_segments(score);
CREATE INDEX IF NOT EXISTS idx_segment_cumulative ON yunnan_physics_score_segments(cumulative_count);

-- ============================================
-- 插入2024年云南省物理类一分一段数据（示例数据，需补充完整）
-- ============================================
-- 注：实际数据需要从官方渠道获取，以下为示例格式

-- INSERT INTO yunnan_physics_score_segments (year, score, count, cumulative_count, notes, data_source)
-- VALUES 
-- (2024, 700, 5, 50, NULL, '官方发布'),
-- (2024, 699, 8, 58, NULL, '官方发布'),
-- (2024, 698, 12, 70, NULL, '官方发布');

-- ============================================
-- 插入2025年云南省物理类一分一段数据（示例数据，需补充完整）
-- ============================================
-- 注：2025年数据待官方发布后录入

-- INSERT INTO yunnan_physics_score_segments (year, score, count, cumulative_count, notes, data_source)
-- VALUES 
-- (2025, 700, 6, 55, NULL, '官方发布'),
-- (2025, 699, 10, 65, NULL, '官方发布');
