# MyBrokenCode 项目任务清单

## 项目概述
AI代码审查应用，支持自定义工作流程、回答格式约束和审查规则，实现个性化精准代码审查。

## 技术栈
- 后端: Python 3.12
- 前端: Vue3 + Electron
- 数据库: SQLite

---

## 阶段一：项目基础架构搭建

### 1. 后端基础架构
- [ ] 创建Python项目结构（使用FastAPI）
- [ ] 配置SQLite数据库连接
- [ ] 设计数据库表结构（AI配置、项目、问题、审查记录等）
- [ ] 实现基础API路由框架
- [ ] 配置CORS支持前端调用

### 2. 前端基础架构
- [ ] 创建Vue3 + Electron项目结构
- [ ] 配置路由（Vue Router）
- [ ] 配置状态管理（Pinia/Vuex）
- [ ] 设计基础UI布局和组件库选择（Element Plus/Ant Design Vue）
- [ ] 配置Electron主进程和渲染进程通信

---

## 阶段二：数据库设计与实现

### 3. 数据库表设计
- [ ] AI配置表（ai_configs）：id, name, api_url, api_key, review_model, recheck_model, stream_enabled, reference_paths, format_paths, workflow_paths, standard_paths, is_active, sort_order, tags, created_at, updated_at
- [ ] 项目表（projects）：id, name, path, sub_paths, tags, default_branch, base_branch, notes, icon, sort_order, created_at, updated_at
- [ ] 问题表（issues）：id, project_id, branch, file_path, line_start, line_end, issue_type, severity, description, code_snippet, status, is_ignored, ignore_type, created_at, updated_at, resolved_at
- [ ] 审查记录表（review_records）：id, project_id, branch, base_branch, review_scope, file_count, issue_count, created_at
- [ ] 对话记录表（chat_history）：id, issue_id, role, content, created_at
- [ ] 项目统计表（project_stats）：project_id, total_reviews, current_issues, resolved_issues, ignored_issues, pending_issues

---

## 阶段三：系统设置 - AI配置页面

### 4. 后端API开发
- [ ] POST /api/ai-configs - 创建AI配置
- [ ] GET /api/ai-configs - 获取所有AI配置
- [ ] GET /api/ai-configs/:id - 获取单个AI配置
- [ ] PUT /api/ai-configs/:id - 更新AI配置
- [ ] DELETE /api/ai-configs/:id - 删除AI配置
- [ ] PUT /api/ai-configs/:id/activate - 激活指定配置
- [ ] PUT /api/ai-configs/reorder - 更新排序
- [ ] POST /api/ai-configs/test-connection - 测试API连接
- [ ] GET /api/ai-configs/:id/models - 获取支持的模型列表

### 5. 前端页面开发
- [ ] 创建AI配置列表页面
- [ ] 实现配置表单（API接口、密钥、模型选择）
- [ ] 实现文件/文件夹选择器（参考资料、回答格式、工作流程、审核标准）
- [ ] 实现拖拽排序功能
- [ ] 实现标签输入组件
- [ ] 实现配置激活/停用切换
- [ ] 实现测试连接功能
- [ ] 实现自动获取模型列表

---

## 阶段四：项目管理页面

### 6. 后端API开发
- [ ] POST /api/projects - 创建项目
- [ ] GET /api/projects - 获取所有项目
- [ ] GET /api/projects/:id - 获取单个项目
- [ ] PUT /api/projects/:id - 更新项目
- [ ] DELETE /api/projects/:id - 删除项目
- [ ] PUT /api/projects/reorder - 更新排序
- [ ] GET /api/projects/:id/branches - 获取项目分支列表
- [ ] GET /api/projects/:id/stats - 获取项目统计信息
- [ ] GET /api/tags - 获取所有已使用的标签

### 7. Git集成
- [ ] 实现Git仓库检测
- [ ] 实现分支列表获取
- [ ] 实现文件变更检测（已提交、暂存、未提交）
- [ ] 实现分支对比功能

### 8. 前端页面开发
- [ ] 创建项目列表页面
- [ ] 实现项目表单（名称、路径、子路径、标签、分支、备注、图标）
- [ ] 实现文件夹/文件选择器
- [ ] 实现标签输入（带提示）
- [ ] 实现拖拽排序
- [ ] 实现项目统计展示
- [ ] 实现图标上传/选择

---

## 阶段五：代码审查页面

### 9. 后端API开发
- [ ] GET /api/issues - 获取问题列表（支持筛选、分页、排序）
- [ ] GET /api/issues/:id - 获取问题详情
- [ ] PUT /api/issues/:id/status - 更新问题状态
- [ ] PUT /api/issues/:id/resolve - 标记问题已解决
- [ ] PUT /api/issues/:id/ignore - 忽略问题
- [ ] POST /api/issues/ignore-similar - 忽略同类问题
- [ ] DELETE /api/issues/:id - 删除问题
- [ ] POST /api/issues/:id/recheck - 复查问题

### 10. 前端页面开发
- [ ] 创建代码审查主页面布局（左侧项目列表 + 右侧内容区）
- [ ] 实现项目列表侧边栏（持久化选择状态）
- [ ] 实现顶部信息栏（分支、统计、筛选）
- [ ] 实现分支切换下拉框（支持搜索）
- [ ] 实现问题卡片列表
- [ ] 实现问题操作按钮（已解决、忽略、忽略同类、复查、删除、查看详情）
- [ ] 实现分页和排序
- [ ] 实现问题筛选功能

---

## 阶段六：问题详情页面

### 11. 后端API开发
- [ ] GET /api/issues/:id/details - 获取问题完整详情
- [ ] GET /api/issues/:id/code - 获取相关代码文件内容
- [ ] POST /api/issues/:id/chat - 发送对话消息
- [ ] GET /api/issues/:id/chat-history - 获取对话历史

### 12. AI对话集成
- [ ] 实现OpenAI格式API调用
- [ ] 实现流式输出支持
- [ ] 实现上下文管理（代码 + 问题 + 对话历史）
- [ ] 实现对话历史存储

### 13. 前端页面开发
- [ ] 创建问题详情页面
- [ ] 实现问题信息展示
- [ ] 实现代码高亮显示（使用highlight.js或Prism.js）
- [ ] 实现AI对话窗口
- [ ] 实现消息发送和接收
- [ ] 实现流式输出显示

---

## 阶段七：分支审查页面

### 14. 后端API开发
- [ ] POST /api/reviews/execute - 执行代码审查
- [ ] GET /api/reviews/:id/progress - 获取审查进度
- [ ] GET /api/reviews/:id/results - 获取审查结果
- [ ] POST /api/reviews/:id/add-issue - 添加问题到问题列表
- [ ] POST /api/reviews/:id/chat - 针对审查结果提问

### 15. AI审查核心功能
- [ ] 实现工作流程文档加载和解析
- [ ] 实现回答格式约束文档加载和解析
- [ ] 实现审查规则与规范文档加载和解析
- [ ] 实现代码变更提取（基于Git diff）
- [ ] 实现AI审查流程执行（按工作流程步骤）
- [ ] 实现审查结果解析（基于回答格式约束）
- [ ] 实现进度追踪和WebSocket推送

### 16. 前端页面开发
- [ ] 创建分支审查页面
- [ ] 实现顶部信息栏（当前分支、基准分支、文件数、审查范围）
- [ ] 实现审查范围选择器
- [ ] 实现执行审查按钮和进度条
- [ ] 实现进度详情展开/折叠
- [ ] 实现审查结果展示
- [ ] 实现结果操作按钮（添加到问题、忽略等）
- [ ] 实现对话框

---

## 阶段八：优化与完善

### 17. 性能优化
- [ ] 实现数据库索引优化
- [ ] 实现API响应缓存
- [ ] 实现大文件分块处理
- [ ] 实现前端虚拟滚动（大列表）

### 18. 用户体验优化
- [ ] 实现加载状态提示
- [ ] 实现错误处理和友好提示
- [ ] 实现操作确认对话框
- [ ] 实现快捷键支持
- [ ] 实现主题切换（明暗模式）

### 19. 测试
- [ ] 编写后端单元测试
- [ ] 编写前端组件测试
- [ ] 进行集成测试
- [ ] 进行用户体验测试

### 20. 文档
- [ ] 编写用户使用手册
- [ ] 编写开发文档
- [ ] 编写API文档
- [ ] 编写部署文档

---

## 优先级说明

**P0（最高优先级）：**
- 阶段一：项目基础架构
- 阶段二：数据库设计
- 阶段三：AI配置页面（核心）
- 阶段四：项目管理页面（核心）

**P1（高优先级）：**
- 阶段七：分支审查页面（核心功能）
- 阶段五：代码审查页面

**P2（中优先级）：**
- 阶段六：问题详情页面
- 阶段八：优化与完善（部分）

**P3（低优先级）：**
- 阶段八：测试和文档

---

## 注意事项

1. **安全性**：API密钥需要加密存储，敏感信息不能明文保存
2. **文件路径处理**：需要兼容Windows和Unix路径格式
3. **Git操作**：需要处理Git命令执行失败的情况
4. **AI调用**：需要处理API超时、限流等异常情况
5. **数据持久化**：用户选择的项目、分支等状态需要持久化
6. **移动端适配**：问题列表采用卡片式设计，需要响应式布局
7. **代码高亮**：需要支持多种编程语言的语法高亮
8. **流式输出**：需要实现WebSocket或SSE支持实时输出
