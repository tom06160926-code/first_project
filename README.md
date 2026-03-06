# 📚 图书管理系统

前后端分离的图书管理系统，支持图书的增删改查、搜索过滤、分页展示和数据统计。

## 🛠 技术栈

- **前端**: React 18 + Ant Design 5 + Axios
- **后端**: Python Flask + Flask-SQLAlchemy + Flask-CORS
- **数据库**: SQLite（开发环境）
- **管理**: npm + concurrently

## 📁 项目结构

```
book-management-system/
├── package.json          # 根目录管理脚本
├── README.md            # 项目说明
├── backend/             # Python 后端
│   ├── app.py          # Flask 主应用
│   ├── requirements.txt # Python 依赖
│   └── database/       # 数据库文件目录
└── frontend/           # React 前端
    ├── package.json
    ├── public/
    └── src/
        ├── index.js
        ├── App.js
        └── components/
            ├── Dashboard.js    # 数据概览
            └── BookList.js     # 图书管理
```

## 🚀 快速开始

### 1. 安装依赖

```bash
npm run install:all
```

### 2. 初始化数据库

```bash
npm run init-db
npm run seed  # 插入示例数据（可选）
```

### 3. 启动开发环境

```bash
npm run dev
```

- 后端: http://localhost:5000
- 前端: http://localhost:3000

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/health | 健康检查 |
| GET | /api/books | 获取图书列表（支持分页、搜索） |
| GET | /api/books/:id | 获取单本图书 |
| POST | /api/books | 创建图书 |
| PUT | /api/books/:id | 更新图书 |
| DELETE | /api/books/:id | 删除图书 |
| GET | /api/categories | 获取分类列表 |
| GET | /api/stats | 获取统计数据 |

## ✨ 功能特性

- 📖 图书 CRUD 管理
- 🔍 多条件搜索（书名/作者/ISBN）
- 📂 分类筛选
- 📊 数据统计面板
- 📄 分页展示
- 🎨 响应式 UI 设计

## 📝 开发说明

### 单独启动后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 单独启动前端

```bash
cd frontend
npm install
npm start
```

### 后端命令

```bash
# 初始化数据库
flask --app app init-db

# 插入示例数据
flask --app app seed
```

## 📄 数据模型

### Book（图书）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String(200) | 书名（必填） |
| author | String(100) | 作者（必填） |
| isbn | String(20) | ISBN（唯一） |
| publisher | String(100) | 出版社 |
| publish_date | Date | 出版日期 |
| category | String(50) | 分类 |
| description | Text | 简介 |
| price | Float | 价格 |
| stock | Integer | 库存 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 🤖 Agent 集群开发

本项目使用 OpenClaw Agent 集群系统自动开发：
- **协调者**: Zoe (OpenClaw)
- **执行 Agent**: Claude Code
- **工作流**: 任务创建 → Agent 执行 → 代码审查 → 自动部署

---

Created with ❤️ by Agent Cluster System
