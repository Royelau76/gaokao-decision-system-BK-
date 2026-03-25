# 开发文档

## 项目架构

### 后端 (Python FastAPI)
```
backend/
├── main.py              # FastAPI主应用
├── requirements.txt     # Python依赖
├── algorithms/          # 推荐算法模块
│   ├── __init__.py
│   └── recommendation.py
└── models/              # 数据模型
    ├── __init__.py
    └── schemas.py
```

### 前端 (React)
```
frontend/
├── src/
│   ├── App.js                    # 主应用组件
│   ├── App.css                   # 全局样式
│   ├── components/               # 组件目录
│   │   ├── StudentForm.js       # 考生信息表单
│   │   ├── RecommendationList.js # 推荐列表
│   │   └── VolunteerTable.js    # 志愿表
│   └── utils/                    # 工具函数
│       └── api.js
└── package.json
```

## 快速开始

### 1. 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
后端服务将运行在 http://localhost:8000

### 2. 启动前端
```bash
cd frontend
npm install
npm start
```
前端将运行在 http://localhost:3000

## API接口

### 1. 获取推荐
```http
POST /api/recommendations
Content-Type: application/json

{
  "score": 640,
  "subjects": ["物理", "化学", "生物"],
  "preference_region": ["上海", "深圳"],
  "preference_major": ["计算机", "人工智能"],
  "risk_tolerance": "稳健"
}
```

### 2. 获取院校列表
```http
GET /api/universities?province=上海&level=985
```

## 推荐算法说明

### 冲稳保划分逻辑

**冲刺层 (20%)**
- 位次范围：考生位次 × 0.7 ~ 考生位次
- 录取概率：30-50%
- 策略：理想院校，可接受调剂

**稳妥层 (50%)**
- 位次范围：考生位次 × 0.9 ~ 考生位次 × 1.1
- 录取概率：50-80%
- 策略：匹配度高的主选志愿

**保底层 (30%)**
- 位次范围：考生位次 ~ 考生位次 × 1.4
- 录取概率：80%+
- 策略：确保不滑档

## 数据导入

### 院校数据格式
```json
{
  "id": "uni_001",
  "name": "南方科技大学",
  "province": "广东",
  "level": "双一流",
  "admission_mode": "综合评价",
  "min_score_2025": 640,
  "min_rank_2025": 1698,
  "majors": [
    {"name": "计算机科学与技术", "code": "080901"},
    {"name": "人工智能", "code": "080717"}
  ]
}
```

### 导入脚本
```bash
python scripts/import_universities.py data/universities.json
```

## 待办事项

- [ ] 完善院校数据库
- [ ] 优化推荐算法
- [ ] 添加数据可视化
- [ ] 支持导出PDF
- [ ] 移动端适配
