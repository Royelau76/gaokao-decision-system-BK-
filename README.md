# 云志选 - 2026云南高考志愿智能决策系统

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Last Commit](https://img.shields.io/github/last-commit/Royelau76/gaokao-decision-system.svg)

## 项目简介
基于Web的2026年云南省高考志愿填报决策支持系统。

## 技术栈
- **前端**: React + Ant Design + ECharts
- **后端**: Python + FastAPI
- **数据库**: SQLite

## 目录结构
```
gaokao-decision-system/
├── frontend/          # React前端
├── backend/           # FastAPI后端
├── data/              # 数据库和原始数据
└── docs/              # 文档
```

## 核心功能
1. 考生信息录入与管理
2. 智能院校专业推荐
3. 冲稳保梯度划分
4. 录取概率预测
5. 志愿表生成与导出

## 快速开始

### 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 启动前端
```bash
cd frontend
npm install
npm start
```

## 数据来源
- 云南省教育考试院
- 各高校招生网
- 教育部学科评估

## 许可证
MIT
