# 云志选系统数据库结构规范

**版本**: v2.0  
**更新日期**: 2026-03-23  
**适用范围**: 云南省高考招生数据管理

---

## 数据库设计原则

1. **数据类型分离**: 计划数据、录取数据、一分一段数据分别存储
2. **年份预留**: 支持2024、2025、2026年数据，未来年份可扩展
3. **批次明确**: 计划数据按批次（B段/C段）分类存储
4. **可追溯性**: 所有表包含 `created_at`、`updated_at`、`data_source` 字段

---

## 数据表清单

| 表名 | 用途 | 数据类型 |
|------|------|---------|
| `yunnan_physics_score_segments` | 一分一段表 | 位次数据 |
| `yunnan_plan_data` | 计划招生数据 | B段/C段招生计划 |
| `yunnan_physics_scores` | 录取数据 | 实际录取分数 |
| `universities` | 学校基础信息 | 学校元数据 |
| `students` | 学生信息 | 用户数据 |
| `volunteer_plans` | 志愿方案 | 用户生成数据 |

---

## 1. 一分一段表 (yunnan_physics_score_segments)

**用途**: 存储云南省高考一分一段表，用于位次换算

**支持年份**: 2024, 2025, 2026(预留)

### 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | 自增ID |
| `year` | INTEGER NOT NULL | 年份 |
| `score` | INTEGER NOT NULL | 高考分数 |
| `count` | INTEGER NOT NULL | 该分数同分人数 |
| `cumulative_count` | INTEGER NOT NULL | 累计人数（位次） |
| `notes` | TEXT | 特殊说明 |
| `created_at` | TIMESTAMP | 创建时间 |
| `updated_at` | TIMESTAMP | 更新时间 |
| `data_source` | TEXT | 数据来源 |

### 唯一约束
```sql
UNIQUE(year, score)
```

### 数据录入规则
- **录入时机**: 每年6月高考成绩公布后
- **数据来源**: 云南省招生考试院官方发布
- **验证要求**: 检查分数连续性、累计人数递增

---

## 2. 计划招生数据表 (yunnan_plan_data) ⭐

**用途**: 统一存储各批次计划招生数据

**支持年份**: 2025, 2026(预留)

**支持批次**:
- `本科批B段` - 普通本科B段计划
- `提前本科批C段` - 提前批C段计划（综合评价等）

### 表结构

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | 自增ID | - |
| `year` | INTEGER NOT NULL | 年份 | 2025 |
| `batch_type` | TEXT NOT NULL | 批次类型 | '本科批B段' / '提前本科批C段' |
| `university_id` | TEXT NOT NULL | 学校标识 | 'tsinghua' |
| `university_name` | TEXT NOT NULL | 学校名称 | '清华大学' |
| `major_group_sequence` | TEXT | 专业组序号 | '01', '02' |
| `major_code` | TEXT | 专业代号 | '001', '002' |
| `major_group_name` | TEXT | 专业组名称 | '物理类' |
| `required_subjects` | TEXT | 选考科目要求 | '物理+化学' |
| `major_category` | TEXT NOT NULL | 专业名称/大类 | '计算机类' |
| `included_majors` | TEXT | 包含专业（大类招生时） | '计算机科学、软件工程' |
| `tuition` | INTEGER | 学费（元/年） | 5000 |
| `enrollment_count` | INTEGER | 招生人数 | 10 |
| `campus` | TEXT | 校区 | '校本部' / '深圳校区' |
| `notes` | TEXT | 备注 | '综合评价，学费7000元' |
| `created_at` | TIMESTAMP | 创建时间 | - |
| `updated_at` | TIMESTAMP | 更新时间 | - |
| `data_source` | TEXT | 数据来源 | - |

### 唯一约束
```sql
UNIQUE(year, batch_type, university_id, major_code, major_category)
```

### 数据录入规则

#### 本科批B段数据录入
```sql
INSERT INTO yunnan_plan_data (
    year, batch_type, university_id, university_name,
    major_group_sequence, major_code, major_group_name,
    required_subjects, major_category, included_majors,
    tuition, enrollment_count, campus, notes
) VALUES (
    2025, '本科批B段', 'tsinghua', '清华大学',
    '01', '001', '物理类',
    '物理+化学', '计算机类', NULL,
    5000, 10, '校本部', '招10人'
);
```

#### 提前本科批C段数据录入
```sql
INSERT INTO yunnan_plan_data (
    year, batch_type, university_id, university_name,
    major_group_sequence, major_code, major_group_name,
    required_subjects, major_category, included_majors,
    tuition, enrollment_count, campus, notes
) VALUES (
    2025, '提前本科批C段', 'shanghaitech', '上海科技大学',
    '99', '01', '物理类',
    '物理+化学', '计算机科学与技术', NULL,
    7000, 1, '校本部', '综合评价，学费7000元'
);
```

### 注意事项
1. **batch_type 必须明确**: 只能是 '本科批B段' 或 '提前本科批C段'
2. **学费单位**: 元/年，整数存储
3. **大类招生**: 使用 `included_majors` 字段列出包含的具体专业
4. **校区信息**: 多校区学校需明确标注

---

## 3. 录取数据表 (yunnan_physics_scores)

**用途**: 存储实际录取数据（含分数、位次）

**支持年份**: 2024, 2025

### 表结构

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | 自增ID | - |
| `university_id` | TEXT NOT NULL | 学校标识 | 'tsinghua' |
| `university_name` | TEXT NOT NULL | 学校名称 | '清华大学' |
| `year` | INTEGER NOT NULL | 年份 | 2024 |
| `major_category` | TEXT NOT NULL | 专业名称 | '计算机类' |
| `major_code` | TEXT | 专业代码 | '0809' |
| `enrollment_count` | INTEGER | 招生人数 | 10 |
| `max_score` | INTEGER | 最高分 | 700 |
| `min_score` | INTEGER NOT NULL | 最低分 | 690 |
| `avg_score` | INTEGER | 平均分 | 695 |
| `min_rank` | INTEGER | 最低位次 | 100 |
| `notes` | TEXT | 备注 | - |
| `created_at` | TIMESTAMP | 创建时间 | - |
| `updated_at` | TIMESTAMP | 更新时间 | - |

### 唯一约束
```sql
UNIQUE(year, university_id, major_category)
```

### 数据录入规则

#### 2024年录取数据（已公布）
```sql
INSERT INTO yunnan_physics_scores (
    university_id, university_name, year, major_category, major_code,
    enrollment_count, max_score, min_score, avg_score, min_rank, notes
) VALUES (
    'tsinghua', '清华大学', 2024, '计算机类', '0809',
    10, 700, 690, 695, 100, NULL
);
```

#### 2025年录取数据（陆续公布中）
- **录入时机**: 每年7-8月录取结束后
- **数据来源**: 云南省招生考试院、各高校官网

### 重要区分
- **计划数据** (`yunnan_plan_data`): 招生前的计划，无实际分数
- **录取数据** (`yunnan_physics_scores`): 录取后的实际数据，必须有分数

---

## 4. 学校基础信息表 (universities)

**用途**: 存储学校基础信息

### 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | TEXT PRIMARY KEY | 学校标识 |
| `name` | TEXT NOT NULL | 学校名称 |
| `province` | TEXT | 所在省份 |
| `city` | TEXT | 所在城市 |
| `level` | TEXT | 层次：985/211/双一流/普通 |
| `admission_mode` | TEXT | 招生模式 |
| `website` | TEXT | 官网 |
| `min_score_2025` | INTEGER | 2025年最低分（缓存） |
| `min_rank_2025` | INTEGER | 2025年最低位次（缓存） |
| `subjects_required` | TEXT | 选科要求 |
| `majors` | TEXT | 主要专业 |
| `advantages` | TEXT | 优势 |
| `disadvantages` | TEXT | 劣势 |

---

## 数据录入流程图

```
用户发送招生数据图片
        ↓
识别数据类型
        ↓
    ┌───┴───┐
    ↓       ↓
计划数据   录取数据
    ↓       ↓
yunnan_   yunnan_physics_
plan_data   scores
    ↓
区分批次
    ↓
┌───┴───┐
↓       ↓
B段     C段
```

---

## 数据验证检查清单

### 计划数据录入后检查
- [ ] `batch_type` 是否为 '本科批B段' 或 '提前本科批C段'
- [ ] `year` 是否正确（2025或2026）
- [ ] `university_id` 是否在 `universities` 表中存在
- [ ] `enrollment_count` 是否为正整数
- [ ] `tuition` 单位是否为元/年

### 录取数据录入后检查
- [ ] `min_score` > 0（必须有实际分数）
- [ ] `year` 是否正确
- [ ] 分数范围是否合理（400-750分）
- [ ] 位次数据是否匹配一分一段表

---

## 历史变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-03-23 | v2.0 | 创建 `yunnan_plan_data` 统一计划数据表，合并B段和C段数据 |
| 2026-03-11 | v1.0 | 初始版本，B段数据单独存储在 `yunnan_b_segment_plans` |

---

*规范制定: 小莫*  
*最后更新: 2026-03-23*
