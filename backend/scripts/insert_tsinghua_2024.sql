-- 清华大学 2024年 云南物理类 招生数据
-- 录入时间: 2026-03-11

-- 确保清华大学在 universities 表中
INSERT OR IGNORE INTO universities (id, name, province, city, level, admission_mode, website, min_score_2025, min_rank_2025, subjects_required, majors, advantages, disadvantages)
VALUES (
    'tsinghua',
    '清华大学',
    '北京',
    '北京',
    '985',
    '统招/强基计划',
    'https://www.tsinghua.edu.cn/',
    NULL,
    NULL,
    '["物理","化学"]',
    '[{"name":"建筑类","code":"0828"},{"name":"工科试验班(智能制造与装备类)","code":"0802"},{"name":"工科试验班(能源与电气类)","code":"0808"},{"name":"电子信息类","code":"0807"},{"name":"计算机类","code":"0809"},{"name":"自动化类","code":"0808"},{"name":"理科试验班(化生类)","code":"0700"},{"name":"工科试验班(秀钟书院)","code":"0800"},{"name":"工科试验班(为先书院)","code":"0800"},{"name":"工科试验班(笃实书院)","code":"0800"},{"name":"理科试验班类(新雅书院)","code":"0700"}]',
    '["国内顶尖工科","清华品牌","强大校友网络","科研实力雄厚"]',
    '["竞争激烈","录取分数极高","学业压力大"]'
);

-- 插入清华大学招生分数线数据
INSERT OR REPLACE INTO yunnan_physics_scores (
    university_id, university_name, year, major_category, major_code,
    enrollment_count, max_score, min_score, avg_score, min_rank, notes
) VALUES 
('tsinghua', '清华大学', 2024, '建筑类', '0828', 1, 701, 701, 701, NULL, NULL),
('tsinghua', '清华大学', 2024, '工科试验班(智能制造与装备类)', '0802', 4, 702, 698, 700, NULL, '招4人'),
('tsinghua', '清华大学', 2024, '工科试验班(能源与电气类)', '0808', 1, 699, 699, 699, NULL, NULL),
('tsinghua', '清华大学', 2024, '电子信息类', '0807', 4, 713, 698, 705, NULL, '招4人'),
('tsinghua', '清华大学', 2024, '计算机类', '0809', 2, 714, 712, 713, NULL, '热门专业'),
('tsinghua', '清华大学', 2024, '自动化类', '0808', 1, 699, 699, 699, NULL, NULL),
('tsinghua', '清华大学', 2024, '理科试验班(化生类)', '0700', 1, 702, 702, 702, NULL, NULL),
('tsinghua', '清华大学', 2024, '工科试验班(秀钟书院)', '0800', 2, 704, 699, 701, NULL, '招2人'),
('tsinghua', '清华大学', 2024, '工科试验班(为先书院)', '0800', 2, 706, 702, 704, NULL, '招2人'),
('tsinghua', '清华大学', 2024, '工科试验班(笃实书院)', '0800', 3, 723, 701, 712, NULL, '最高分723，招3人'),
('tsinghua', '清华大学', 2024, '理科试验班类(新雅书院)', '0700', 1, 718, 718, 718, NULL, '新雅书院');
