# MyBrokenCode 项目开发总结

## 项目概述

MyBrokenCode 是一款基于 AI 的代码审查应用，支持用户自定义工作流程、回答格式约束和审查规则，实现个性化、精准的代码审查功能。

## 已完成功能

### 1. 后端开发 (Python FastAPI)

#### 核心文件
- **main.py** - FastAPI 主应用，包含所有 REST API 端点
- **database.py** - SQLAlchemy 数据库模型和连接管理
- **schemas.py** - Pydantic 数据验证模型
- **git_service.py** - Git 仓库集成服务
- **ai_service.py** - AI 代码审查核心服务

#### API 端点
- AI 配置管理：创建、读取、更新、删除、激活配置
- 项目管理：CRUD 操作、获取分支列表
- 问题管理：CRUD 操作、状态更新、标记已解决
- 代码审查：执行 AI 审查、获取审查结果

#### 数据库设计
- `ai_configs` - AI 配置表
- `projects` - 项目信息表
- `issues` - 问题记录表
- `review_records` - 审查记录表
- `chat_history` - 对话历史表
- `project_stats` - 项目统计表

### 2. 前端开发 (Vue3 + Electron)

#### 页面组件
- **AIConfig.vue** - AI 配置管理页面
  - 配置列表展示
  - 添加/编辑配置表单
  - 激活/删除配置
  - 支持配置 API 地址、密钥、模型选择

- **Projects.vue** - 项目管理页面
  - 项目列表展示
  - 添加/编辑项目表单
  - 标签输入（按回车添加）
  - 项目路径、分支配置

- **Review.vue** - 代码审查页面
  - 左侧项目列表（持久化选择）
  - 问题卡片列表
  - 问题状态筛选
  - 统计数据展示
  - 已解决/忽略/删除操作

- **BranchReview.vue** - 分支审查页面（核心功能）
  - 项目和分支选择
  - 审查范围设置（已提交、暂存、未提交、全部）
  - 执行 AI 审查
  - 实时进度显示
  - 审查结果展示
  - 添加到问题列表

#### UI/UX 设计系统
- **配色方案**：Trust Blue (#2563EB) + Orange CTA (#F97316)
- **字体系统**：Poppins (标题) + Open Sans (正文)
- **设计风格**：现代简约、开发者友好、深色侧边栏
- **响应式布局**：支持桌面和移动端

### 3. 核心功能实现

#### AI 审查流程
1. 加载用户自定义的工作流程文档
2. 加载回答格式约束文档
3. 加载审查规则与规范文档
4. 获取 Git 代码变更
5. 调用 AI API 执行审查
6. 解析审查结果
7. 保存审查记录

#### Git 集成
- 获取仓库分支列表
- 获取当前分支
- 获取文件变更（支持多种范围）
- 读取文件内容

#### 数据持久化
- SQLite 数据库自动创建
- 用户选择状态持久化（localStorage）
- 审查记录和问题追踪

## 技术栈

### 后端
- Python 3.12
- FastAPI - 现代高性能 Web 框架
- SQLAlchemy - ORM
- Pydantic - 数据验证
- GitPython - Git 集成
- httpx - 异步 HTTP 客户端

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- Electron - 跨平台桌面应用
- Element Plus - UI 组件库
- Vite - 构建工具
- Axios - HTTP 客户端
- Vue Router - 路由管理
- Pinia - 状态管理

## 项目结构

```
MyBrokenCode/
├── backend/
│   ├── main.py              # FastAPI 主应用
│   ├── database.py          # 数据库模型
│   ├── schemas.py           # Pydantic 模型
│   ├── git_service.py       # Git 服务
│   ├── ai_service.py        # AI 服务
│   └── requirements.txt     # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── AIConfig.vue
│   │   │   ├── Projects.vue
│   │   │   ├── Review.vue
│   │   │   └── BranchReview.vue
│   │   ├── api/index.js     # API 客户端
│   │   ├── router/index.js  # 路由配置
│   │   ├── App.vue          # 主组件
│   │   └── main.js          # 入口文件
│   ├── electron/main.js     # Electron 主进程
│   ├── package.json
│   └── vite.config.js
├── 工作流程/                # 工作流程文档目录
├── 回答格式约束/            # 回答格式约束文档目录
├── 审查规则与规范/          # 审查规则与规范文档目录
├── README.md                # 项目文档
└── TASK-TODO.md             # 任务清单
```

## 如何运行

### 后端
```bash
cd backend
pip install -r requirements.txt
python main.py
```
后端运行在 http://localhost:8000

### 前端
```bash
cd frontend
npm install
npm run dev              # Web 版
npm run electron:dev     # 桌面应用
```
前端运行在 http://localhost:5173

## 待开发功能

1. **问题详情页面** - 详细展示问题信息和代码片段
2. **AI 对话功能** - 针对问题进行 AI 对话
3. **文件路径选择器** - Electron 原生文件/文件夹选择对话框
4. **拖拽排序** - AI 配置和项目的拖拽排序
5. **流式输出** - 实时显示 AI 审查过程
6. **WebSocket** - 实时进度推送

## 设计亮点

1. **模块化架构** - 前后端分离，职责清晰
2. **专业 UI/UX** - 基于设计系统的现代化界面
3. **灵活配置** - 支持多个 AI 配置，用户自定义审查规则
4. **Git 集成** - 深度集成 Git，支持多种审查范围
5. **数据持久化** - 完整的数据库设计，支持历史追踪
6. **跨平台** - 支持 Web 和桌面应用

## 核心价值

MyBrokenCode 的核心价值在于：
- **个性化**：用户可以自定义工作流程、格式约束和审查标准
- **精准**：基于 AI 的智能代码审查，结合用户规范
- **高效**：自动化审查流程，节省人工审查时间
- **可追踪**：完整的问题管理和审查记录

## 总结

项目已完成核心功能的开发，包括完整的前后端架构、AI 审查核心功能、专业的 UI/UX 设计。系统可以正常运行，支持 AI 配置管理、项目管理、代码审查和分支审查等核心功能。

下一步可以继续完善问题详情页面、AI 对话功能、文件选择器等增强功能，进一步提升用户体验。
