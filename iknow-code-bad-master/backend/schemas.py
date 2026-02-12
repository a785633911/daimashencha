from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AIConfigBase(BaseModel):
    name: str
    api_url: str
    api_key: str
    review_model: Optional[str] = None
    recheck_model: Optional[str] = None
    stream_enabled: bool = False
    reference_paths: Optional[List[str]] = []
    format_paths: Optional[List[str]] = []
    workflow_paths: Optional[List[str]] = []
    standard_paths: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class AIConfigCreate(AIConfigBase):
    pass

class AIConfigUpdate(AIConfigBase):
    pass

class AIConfigResponse(AIConfigBase):
    id: int
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    path: str
    sub_paths: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    default_branch: Optional[str] = None
    base_branch: Optional[str] = None
    notes: Optional[str] = None
    icon: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IssueBase(BaseModel):
    project_id: int
    branch: Optional[str] = None
    file_path: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    issue_type: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    code_snippet: Optional[str] = None
    status: str = "待审核"

class IssueCreate(IssueBase):
    pass

class IssueUpdate(BaseModel):
    status: Optional[str] = None
    is_ignored: Optional[bool] = None
    ignore_type: Optional[str] = None
    issue_type: Optional[str] = None
    severity: Optional[str] = None

class IssueResponse(IssueBase):
    id: int
    is_ignored: bool
    ignore_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    content: str
