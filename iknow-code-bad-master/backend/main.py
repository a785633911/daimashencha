from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import database
import schemas
from datetime import datetime
import asyncio
import uuid


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

app = FastAPI(title="MyBrokenCode API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- AI Config endpoints ----------

@app.post("/api/ai-configs", response_model=schemas.AIConfigResponse)
def create_ai_config(config: schemas.AIConfigCreate, db: Session = Depends(database.get_db)):
    db_config = database.AIConfig(**config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@app.get("/api/ai-configs", response_model=List[schemas.AIConfigResponse])
def get_ai_configs(db: Session = Depends(database.get_db)):
    return db.query(database.AIConfig).order_by(database.AIConfig.sort_order).all()

@app.get("/api/ai-configs/{config_id}", response_model=schemas.AIConfigResponse)
def get_ai_config(config_id: int, db: Session = Depends(database.get_db)):
    config = db.query(database.AIConfig).filter(database.AIConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config

@app.put("/api/ai-configs/{config_id}", response_model=schemas.AIConfigResponse)
def update_ai_config(config_id: int, config: schemas.AIConfigUpdate, db: Session = Depends(database.get_db)):
    db_config = db.query(database.AIConfig).filter(database.AIConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Config not found")
    for key, value in config.model_dump().items():
        setattr(db_config, key, value)
    db_config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_config)
    return db_config

@app.delete("/api/ai-configs/{config_id}")
def delete_ai_config(config_id: int, db: Session = Depends(database.get_db)):
    db_config = db.query(database.AIConfig).filter(database.AIConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Config not found")
    db.delete(db_config)
    db.commit()
    return {"message": "Config deleted"}

@app.put("/api/ai-configs/{config_id}/activate")
def activate_ai_config(config_id: int, db: Session = Depends(database.get_db)):
    db.query(database.AIConfig).update({"is_active": False})
    db_config = db.query(database.AIConfig).filter(database.AIConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Config not found")
    db_config.is_active = True
    db.commit()
    return {"message": "Config activated"}

@app.put("/api/ai-configs/reorder")
def reorder_ai_configs(order: List[int], db: Session = Depends(database.get_db)):
    for idx, config_id in enumerate(order):
        db.query(database.AIConfig).filter(database.AIConfig.id == config_id).update({"sort_order": idx})
    db.commit()
    return {"message": "Reordered"}

@app.get("/api/ai-configs/{config_id}/models")
async def get_ai_models(config_id: int, db: Session = Depends(database.get_db)):
    import httpx
    config = db.query(database.AIConfig).filter(database.AIConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    try:
        headers = {"Authorization": f"Bearer {config.api_key}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{config.api_url}/models", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            models = sorted([m["id"] for m in data.get("data", []) if "id" in m])
            return {"models": models}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel as PydanticBaseModel

class FetchModelsRequest(PydanticBaseModel):
    api_url: str
    api_key: str

@app.post("/api/ai-configs/fetch-models")
async def fetch_models_direct(req: FetchModelsRequest):
    import httpx
    try:
        headers = {"Authorization": f"Bearer {req.api_key}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{req.api_url}/models", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            models = sorted([m["id"] for m in data.get("data", []) if "id" in m])
            return {"models": models}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FetchBranchesRequest(PydanticBaseModel):
    path: str

@app.post("/api/projects/fetch-branches")
def fetch_branches_direct(req: FetchBranchesRequest):
    from git_service import GitService
    branches = GitService.get_branches(req.path)
    current = GitService.get_current_branch(req.path)
    return {"branches": branches, "current": current}

@app.post("/api/projects/fetch-remote-branches")
def fetch_remote_branches(data: dict, db: Session = Depends(database.get_db)):
    from git_service import GitService
    project_id = data.get("project_id")
    project = db.query(database.Project).filter(database.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    branches = GitService.get_remote_branches(project.path)
    return {"branches": branches}

@app.post("/api/projects/git-status")
def get_git_status(data: dict, db: Session = Depends(database.get_db)):
    from git_service import GitService
    project_id = data.get("project_id")
    branch = data.get("branch", "main")
    base_branch = data.get("base_branch", "main")

    project = db.query(database.Project).filter(database.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    status = GitService.get_git_status(project.path, branch, base_branch)
    return status

@app.post("/api/projects/get-changed-files")
def get_changed_files(data: dict):
    from git_service import GitService
    repo_path = data.get("repo_path")
    base_branch = data.get("base_branch", "main")
    target_branch = data.get("target_branch", "main")
    scope = data.get("scope", "all")

    if not repo_path:
        raise HTTPException(status_code=400, detail="repo_path is required")

    files = GitService.get_changed_files(repo_path, base_branch, target_branch, scope)
    return {"files": files}

@app.post("/api/projects/get-file-content")
def get_file_content(data: dict):
    from git_service import GitService
    repo_path = data.get("repo_path")
    file_path = data.get("file_path")
    branch = data.get("branch", "main")

    if not repo_path or not file_path:
        raise HTTPException(status_code=400, detail="repo_path and file_path are required")

    content = GitService.get_file_content(repo_path, file_path)
    return {"content": content}

# ---------- Project endpoints ----------

@app.post("/api/projects", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    db_project = database.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    stats = database.ProjectStats(project_id=db_project.id)
    db.add(stats)
    db.commit()
    return db_project

@app.get("/api/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(database.get_db)):
    return db.query(database.Project).order_by(database.Project.sort_order).all()

@app.get("/api/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(database.Project).filter(database.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/api/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(database.get_db)):
    db_project = db.query(database.Project).filter(database.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    db_project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    db_project = db.query(database.Project).filter(database.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted"}

@app.put("/api/projects/reorder")
def reorder_projects(order: List[int], db: Session = Depends(database.get_db)):
    for idx, pid in enumerate(order):
        db.query(database.Project).filter(database.Project.id == pid).update({"sort_order": idx})
    db.commit()
    return {"message": "Reordered"}

@app.get("/api/projects/{project_id}/branches")
def get_project_branches(project_id: int, db: Session = Depends(database.get_db)):
    from git_service import GitService
    project = db.query(database.Project).filter(database.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    branches = GitService.get_branches(project.path)
    current = GitService.get_current_branch(project.path)
    return {"branches": branches, "current": current}

@app.get("/api/projects/{project_id}/stats")
def get_project_stats(project_id: int, db: Session = Depends(database.get_db)):
    total = db.query(database.Issue).filter(database.Issue.project_id == project_id).count()
    resolved = db.query(database.Issue).filter(
        database.Issue.project_id == project_id,
        database.Issue.status.in_(["已解决", "已完成", "resolved"]),
        database.Issue.is_ignored == False
    ).count()
    ignored = db.query(database.Issue).filter(database.Issue.project_id == project_id, database.Issue.is_ignored == True).count()
    pending = db.query(database.Issue).filter(
        database.Issue.project_id == project_id,
        database.Issue.status.in_(["待解决", "pending"]),
        database.Issue.is_ignored == False
    ).count()
    reviews = db.query(database.ReviewRecord).filter(database.ReviewRecord.project_id == project_id).count()
    return {"total_issues": total, "resolved": resolved, "ignored": ignored, "pending": pending, "total_reviews": reviews}

@app.post("/api/projects/{project_id}/full-stats")
def get_project_full_stats(project_id: int, data: dict, db: Session = Depends(database.get_db)):
    """
    获取项目完整统计信息，包括git状态、文件统计和问题统计
    """
    from git_service import GitService

    project = db.query(database.Project).filter(database.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    base_branch = data.get("base_branch", project.base_branch or "main")

    # 获取当前分支
    current_branch = GitService.get_current_branch(project.path)

    # 获取git状态（包含所有变更：已提交、暂存、未提交）
    git_status = GitService.get_git_status(project.path, current_branch, base_branch)

    # 获取问题统计
    total_issues = db.query(database.Issue).filter(database.Issue.project_id == project_id).count()
    resolved_issues = db.query(database.Issue).filter(
        database.Issue.project_id == project_id,
        database.Issue.status.in_(["已解决", "已完成", "resolved"]),
        database.Issue.is_ignored == False
    ).count()
    ignored_issues = db.query(database.Issue).filter(
        database.Issue.project_id == project_id,
        database.Issue.is_ignored == True
    ).count()
    pending_issues = db.query(database.Issue).filter(
        database.Issue.project_id == project_id,
        database.Issue.status.in_(["待解决", "pending"]),
        database.Issue.is_ignored == False
    ).count()
    total_reviews = db.query(database.ReviewRecord).filter(
        database.ReviewRecord.project_id == project_id
    ).count()

    return {
        "current_branch": current_branch,
        "base_branch": base_branch,
        "git_status": {
            "staged_commits": git_status.get("staged_commits", 0),
            "modified_files": git_status.get("modified_files", 0),
            "added_files": git_status.get("added_files", 0),
            "deleted_files": git_status.get("deleted_files", 0)
        },
        "issue_stats": {
            "total": total_issues,
            "pending": pending_issues,
            "resolved": resolved_issues,
            "ignored": ignored_issues
        },
        "review_stats": {
            "total_reviews": total_reviews
        }
    }

@app.get("/api/tags")
def get_all_tags(db: Session = Depends(database.get_db)):
    projects = db.query(database.Project).all()
    tags = set()
    for p in projects:
        if p.tags:
            for t in p.tags:
                tags.add(t)
    configs = db.query(database.AIConfig).all()
    for c in configs:
        if c.tags:
            for t in c.tags:
                tags.add(t)
    return {"tags": sorted(tags)}

# ---------- Issue endpoints ----------

@app.post("/api/issues", response_model=schemas.IssueResponse)
def create_issue(issue: schemas.IssueCreate, db: Session = Depends(database.get_db)):
    db_issue = database.Issue(**issue.model_dump())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

@app.get("/api/issues", response_model=List[schemas.IssueResponse])
def get_issues(
    project_id: int = None,
    status: str = None,
    severity: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(database.get_db)
):
    from starlette.responses import JSONResponse
    query = db.query(database.Issue)
    if project_id:
        query = query.filter(database.Issue.project_id == project_id)
    status_aliases = {
        "待审核": ["待审核", "待审批", "pending_review"],
        "待排期": ["待排期", "scheduled"],
        "待解决": ["待解决", "pending"],
        "修改中": ["修改中", "in_progress"],
        "待复查": ["待复查", "pending_recheck"],
        "已解决": ["已解决", "已完成", "resolved"]
    }
    if status:
        if status == "已忽略":
            query = query.filter(
                (database.Issue.is_ignored == True) | (database.Issue.status == "已忽略")
            )
        elif status in status_aliases:
            query = query.filter(
                database.Issue.status.in_(status_aliases[status]),
                database.Issue.is_ignored == False
            )
        else:
            query = query.filter(database.Issue.status == status)
    if severity:
        query = query.filter(database.Issue.severity == severity)

    # Get total count
    total = query.count()

    # Apply pagination
    issues = query.order_by(database.Issue.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # Add total count to response headers
    return JSONResponse(
        content=[schemas.IssueResponse.model_validate(issue).model_dump(mode='json') for issue in issues],
        headers={
            "X-Total-Count": str(total),
            "Access-Control-Expose-Headers": "X-Total-Count"
        }
    )

@app.get("/api/issues/{issue_id}", response_model=schemas.IssueResponse)
def get_issue(issue_id: int, db: Session = Depends(database.get_db)):
    issue = db.query(database.Issue).filter(database.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@app.get("/api/issues/{issue_id}/code")
def get_issue_code(issue_id: int, db: Session = Depends(database.get_db)):
    from git_service import GitService
    issue = db.query(database.Issue).filter(database.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    project = db.query(database.Project).filter(database.Project.id == issue.project_id).first()
    if not project or not issue.file_path:
        return {"code": "", "file_path": ""}
    code = GitService.get_file_content(project.path, issue.file_path)
    return {"code": code, "file_path": issue.file_path}

@app.put("/api/issues/{issue_id}/status")
def update_issue_status(issue_id: int, update: schemas.IssueUpdate, db: Session = Depends(database.get_db)):
    issue = db.query(database.Issue).filter(database.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if update.status:
        if update.status == "已忽略":
            issue.status = "已忽略"
            issue.is_ignored = True
            if update.ignore_type:
                issue.ignore_type = update.ignore_type
            elif not issue.ignore_type:
                issue.ignore_type = "manual"
        elif update.status == "已解决":
            issue.status = "已解决"
            issue.is_ignored = False
            issue.ignore_type = None
        else:
            issue.status = update.status
            issue.is_ignored = False
            if update.ignore_type:
                issue.ignore_type = update.ignore_type
            else:
                issue.ignore_type = None
    elif update.is_ignored is not None:
        issue.is_ignored = update.is_ignored
        if update.is_ignored:
            issue.status = "已忽略"
            if update.ignore_type:
                issue.ignore_type = update.ignore_type
            elif not issue.ignore_type:
                issue.ignore_type = "manual"
        else:
            if issue.status == "已忽略":
                issue.status = "待审核"
            if update.ignore_type:
                issue.ignore_type = update.ignore_type
            else:
                issue.ignore_type = None
    elif update.ignore_type:
        issue.ignore_type = update.ignore_type
    issue.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Issue updated"}

@app.put("/api/issues/{issue_id}")
def update_issue(issue_id: int, update: schemas.IssueUpdate, db: Session = Depends(database.get_db)):
    issue = db.query(database.Issue).filter(database.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(issue, key, value)
    issue.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Issue updated"}

@app.put("/api/issues/{issue_id}/resolve")
def resolve_issue(issue_id: int, db: Session = Depends(database.get_db)):
    issue = db.query(database.Issue).filter(database.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.status = "已解决"
    issue.is_ignored = False
    issue.ignore_type = None
    issue.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": "Issue resolved"}

@app.put("/api/issues/{issue_id}/ignore")
def ignore_issue(issue_id: int, db: Session = Depends(database.get_db)):
    issue = db.query(database.Issue).filter(database.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.is_ignored = True
    issue.ignore_type = "manual"
    issue.status = "已忽略"
    issue.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Issue ignored"}

@app.post("/api/issues/ignore-similar")
def ignore_similar_issues(issue_type: str, project_id: int, db: Session = Depends(database.get_db)):
    db.query(database.Issue).filter(
        database.Issue.project_id == project_id,
        database.Issue.issue_type == issue_type
    ).update({"is_ignored": True, "ignore_type": "similar", "status": "已忽略"})
    db.commit()
    return {"message": "Similar issues ignored"}

@app.delete("/api/issues/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(database.get_db)):
    issue = db.query(database.Issue).filter(database.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    db.delete(issue)
    db.commit()
    return {"message": "Issue deleted"}

# ---------- Chat endpoints ----------

@app.post("/api/issues/{issue_id}/chat")
async def chat_with_issue(issue_id: int, message: schemas.ChatMessage, db: Session = Depends(database.get_db)):
    import httpx
    from git_service import GitService
    issue = db.query(database.Issue).filter(database.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    config = db.query(database.AIConfig).filter(database.AIConfig.is_active == True).first()
    if not config:
        raise HTTPException(status_code=404, detail="No active AI config")
    user_msg = database.ChatHistory(issue_id=issue_id, role="user", content=message.content)
    db.add(user_msg)
    db.commit()
    history = db.query(database.ChatHistory).filter(database.ChatHistory.issue_id == issue_id).order_by(database.ChatHistory.created_at).all()
    messages = []
    project = db.query(database.Project).filter(database.Project.id == issue.project_id).first()
    code = ""
    if project and issue.file_path:
        code = GitService.get_file_content(project.path, issue.file_path)
    sys_content = f"You are a code review assistant.\nIssue type: {issue.issue_type}\nSeverity: {issue.severity}\nDescription: {issue.description}\nFile: {issue.file_path}\n"
    if code:
        sys_content += f"\nCode:\n```\n{code}\n```"
    messages.append({"role": "system", "content": sys_content})
    for h in history:
        messages.append({"role": h.role, "content": h.content})
    headers = {"Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"}
    payload = {"model": config.recheck_model or config.review_model, "messages": messages}
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{config.api_url}/chat/completions", headers=headers, json=payload)
            try:
                data = resp.json()
            except Exception:
                data = None

            if resp.status_code >= 400:
                error_message = None
                if isinstance(data, dict):
                    error_message = (data.get("error") or {}).get("message") or data.get("detail") or data.get("message")
                if not error_message:
                    error_message = resp.text
                reply = f"AI response error: {error_message}"
            else:
                reply = None
                if isinstance(data, dict):
                    choices = data.get("choices")
                    if choices and isinstance(choices, list):
                        first = choices[0] or {}
                        message = first.get("message") or {}
                        reply = message.get("content") or first.get("text")
                    if not reply:
                        reply = data.get("reply") or data.get("message")
                if not reply:
                    reply = "AI response error: empty reply"
    except Exception as e:
        reply = f"AI response error: {str(e)}"
    ai_msg = database.ChatHistory(issue_id=issue_id, role="assistant", content=reply)
    db.add(ai_msg)
    db.commit()
    return {"reply": reply}

@app.get("/api/issues/{issue_id}/chat-history")
def get_chat_history(issue_id: int, db: Session = Depends(database.get_db)):
    history = db.query(database.ChatHistory).filter(database.ChatHistory.issue_id == issue_id).order_by(database.ChatHistory.created_at).all()
    return [{"role": h.role, "content": h.content, "created_at": h.created_at.isoformat()} for h in history]

# ---------- Review endpoints ----------

@app.post("/api/reviews/execute")
async def execute_review(project_id: int, base_branch: str, target_branch: str, scope: str, db: Session = Depends(database.get_db)):
    from ai_service import AIService
    from git_service import GitService

    # 获取项目
    project = db.query(database.Project).filter(database.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 获取AI配置
    config = db.query(database.AIConfig).filter(database.AIConfig.is_active == True).first()
    if not config:
        raise HTTPException(status_code=404, detail="No active AI config")

    # 初始化AI服务
    ai_service = AIService(config.api_url, config.api_key, config.review_model, config.stream_enabled)

    # 加载文档
    workflow_docs = config.workflow_paths or []
    format_docs = config.format_paths or []
    standard_docs = config.standard_paths or []

    workflow = ai_service.load_documents(workflow_docs)
    format_constraint = ai_service.load_documents(format_docs)
    standards = ai_service.load_documents(standard_docs)

    # 获取变更文件列表
    changed_files = GitService.get_changed_files(project.path, base_branch, target_branch, scope)

    # 构建详细的初始化信息
    init_details = {
        "project_name": project.name,
        "project_path": project.path,
        "ai_config": config.name,
        "review_model": config.review_model,
        "workflow_docs": workflow_docs,
        "format_docs": format_docs,
        "standard_docs": standard_docs,
        "workflow_loaded": len(workflow) > 0,
        "format_loaded": len(format_constraint) > 0,
        "standards_loaded": len(standards) > 0
    }

    # 文件列表详情
    file_details = {
        "total_files": len(changed_files),
        "files": [{"path": f['path'], "status": f['status']} for f in changed_files[:10]]
    }

    # 执行审查
    results = []
    analysis_details = []

    for idx, file_info in enumerate(changed_files[:10]):
        file_path = file_info['path']
        try:
            code = GitService.get_file_content(project.path, file_path)
            if code:
                review_result = await ai_service.review_code(code, file_path, workflow, format_constraint, standards)
                issues = ai_service.parse_review_result(review_result['content'])
                results.extend(issues)

                analysis_details.append({
                    "file": file_path,
                    "status": "success",
                    "issues_found": len(issues),
                    "message": f"分析完成，发现 {len(issues)} 个问题"
                })
            else:
                analysis_details.append({
                    "file": file_path,
                    "status": "skipped",
                    "issues_found": 0,
                    "message": "文件内容为空，跳过"
                })
        except Exception as e:
            analysis_details.append({
                "file": file_path,
                "status": "error",
                "issues_found": 0,
                "message": f"分析失败: {str(e)}"
            })

    # 保存审查记录
    record = database.ReviewRecord(
        project_id=project_id, branch=target_branch, base_branch=base_branch,
        review_scope=scope, file_count=len(changed_files), issue_count=len(results)
    )
    db.add(record)
    db.commit()

    return {
        "results": results,
        "file_count": len(changed_files),
        "init_details": init_details,
        "file_details": file_details,
        "analysis_details": analysis_details
    }

# ---------- WebSocket endpoints ----------

from websocket_manager import manager
from task_manager import task_manager
from review_processor import review_processor

@app.websocket("/ws/review/{connection_id}")
async def websocket_review_endpoint(websocket: WebSocket, connection_id: str):
    """WebSocket端点用于实时代码审查"""
    await manager.connect(websocket, connection_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "start_review":
                # 启动审查任务
                project_id = data.get("project_id")
                base_branch = data.get("base_branch")
                target_branch = data.get("target_branch")
                scope = data.get("scope", "all")
                specific_files = data.get("specific_files")

                # 创建任务
                task = task_manager.create_task(project_id, base_branch, target_branch, scope, specific_files)
                manager.bind_task(task.task_id, connection_id)

                # 返回任务ID
                await websocket.send_json({
                    "type": "task_created",
                    "task_id": task.task_id
                })

                # 获取数据库会话
                db = next(database.get_db())

                try:
                    # 获取项目和配置
                    project = db.query(database.Project).filter(database.Project.id == project_id).first()
                    if not project:
                        await websocket.send_json({
                            "type": "error",
                            "message": "项目不存在"
                        })
                        continue

                    config = db.query(database.AIConfig).filter(database.AIConfig.is_active == True).first()
                    if not config:
                        await websocket.send_json({
                            "type": "error",
                            "message": "没有激活的AI配置"
                        })
                        continue

                    # 在后台执行审查
                    asyncio.create_task(review_processor.process_review(task.task_id, project, config, db))

                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"启动审查失败: {str(e)}"
                    })
                finally:
                    db.close()

            elif message_type == "cancel_review":
                # 取消审查
                task_id = data.get("task_id")
                task = task_manager.get_task(task_id)
                if task:
                    task.cancel()
                    await websocket.send_json({
                        "type": "cancelled",
                        "task_id": task_id
                    })

            elif message_type == "get_task_status":
                # 获取任务状态
                task_id = data.get("task_id")
                task = task_manager.get_task(task_id)
                if task:
                    await websocket.send_json({
                        "type": "task_status",
                        "task": task.to_dict(),
                        "results": task.results,
                        "errors": task.errors
                    })

            elif message_type == "ping":
                # 心跳
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(connection_id)

@app.get("/api/reviews/tasks/{task_id}")
def get_task_status(task_id: str):
    """获取任务状态（HTTP接口，用于轮询备份）"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task": task.to_dict(),
        "results": task.results,
        "errors": task.errors
    }

@app.delete("/api/reviews/tasks/{task_id}")
def cancel_task(task_id: str):
    """取消任务"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.cancel()
    return {"message": "Task cancelled"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
