# major_outcomes 数据录入格式与字段说明

## 简化录入格式

只填核心字段，其余自动补默认值：

```
uni_id | major_category | year | employment_rate | 官方? | salary_range | 估算? | grad_rate | 官方? | top_employers | 来源
```

## 完整录入格式

```
uni_id | major_category | year | employment_rate | employment_rate_official | employment_rate_definition | salary_range | salary_estimated | salary_source | grad_rate | grad_rate_official | grad_rate_note | top_employers | employer_source | data_confidence
```

## 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `uni_id` | TEXT | 院校ID，对应 universities 表 | `seu`, `hust`, `hit` |
| `major_category` | TEXT | **Layer 1 大类**，不是细分专业 | `计算机类`, `电子信息类`, `自动化类` |
| `year` | INT | 数据年份 | `2025` |
| `employment_rate` | DECIMAL | 就业率（百分比数字） | `96.3` 表示 96.3% |
| `employment_rate_official` | 0/1 | L1 学校官方？1=官方发布, 0=行业/第三方 | `1` |
| `employment_rate_definition` | TEXT | 就业口径（可选） | `含灵活就业`, `仅签约就业` |
| `salary_range` | TEXT | **薪资区间**，不是单点数字 | `12000-15000`, `15000-18000`, `18000+` |
| `salary_estimated` | 0/1 | L3 估算？1=行业估算/薪酬网, 0=学校官方 | `1` |
| `salary_source` | TEXT | 薪资数据来源 | `薪酬网`, `学校官方` |
| `grad_rate` | DECIMAL | 深造率（保研+考研+出国） | `58.0` 表示 58% |
| `grad_rate_official` | 0/1 | L1 学校官方？ | `1` |
| `grad_rate_note` | TEXT | 深造口径备注（可选） | `含保研+考研+出国`, `仅国内升学` |
| `top_employers` | TEXT | 主要去向，逗号分隔 | `华为,腾讯,字节跳动` |
| `employer_source` | TEXT | 去向数据来源 | `学校就业质量报告` |
| `data_confidence` | TEXT | 整体置信等级 | `L1` / `L2` / `L3` |

## 可用 salary_range 区间

```
18000+
15000-18000
12000-15000
9000-12000
6000-9000
0-6000
```

## 可用 Layer 1 大类（major_category 值）

```
计算机类
电子信息类
自动化类
电气类
机械类
材料类
半导体类
能源动力类
航空航天类
土木类
化学化工类
数学类
物理类
经济管理类
医学类
生物类
环境类
法学类
心理学
天文地理类
力学类
海洋类
交通运输类
工科综合类
理学综合类
```

## 三层可信度体系

| 层级 | 置信度 | 适用字段 | 说明 |
|------|--------|----------|------|
| **L1** | 最高 | employment_rate, grad_rate | 学校官方发布，口径明确 |
| **L2** | 中等 | top_employers, salary_range | 行业统计/第三方报告 |
| **L3** | 低 | salary_range（估算） | 薪酬网/模型推算，仅供参考 |

前端展示效果：

```
平均薪资：12000-15000 元（行业估算）
就业率：96.3%（学校官方）
深造率：58.0%（学校官方）
```

## 填写示例

**最简版（推荐）**：

```
sysu | 计算机类 | 2025 | 96.8 | 1 | 12000-15000 | 1 | 55.0 | 1 | 华为,腾讯,字节跳动,阿里 | 学校就业质量报告
sysu | 电子信息类 | 2025 | 97.2 | 1 | 12000-15000 | 1 | 60.5 | 0 | 华为,中兴,小米 | 学校就业质量报告
sysu | 医学类 | 2025 | 95.0 | 1 | 9000-12000 | 1 | 70.0 | 1 | 各级医院,药企 | 学校就业报告
sysu | 法学类 | 2025 | 90.5 | 1 | 6000-9000 | 1 | 45.0 | 1 | 律所,法院,企业法务 | 学校就业报告
```

**带口径说明版**：

```
hust | 计算机类 | 2025 | 97.5 | 0 | 含灵活就业 | 15000-18000 | 1 | 薪酬网 | 66.0 | 0 | 仅国内升学 | 华为,腾讯,字节跳动,阿里云,百度 | 华中科技大学就业质量报告 | L2
```