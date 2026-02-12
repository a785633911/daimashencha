import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ReviewPhase(Enum):
    INIT = "init"
    FILE_GROUPING = "file_grouping"
    QUICK_SCAN = "quick_scan"
    DEEP_ANALYSIS = "deep_analysis"
    GENERATING_REPORT = "generating_report"
    COMPLETE = "complete"

class ReviewTask:
    def __init__(self, task_id: str, project_id: int, base_branch: str, target_branch: str, scope: str, specific_files: Optional[List[str]] = None):
        self.task_id = task_id
        self.project_id = project_id
        self.base_branch = base_branch
        self.target_branch = target_branch
        self.scope = scope
        self.specific_files = specific_files
        self.status = TaskStatus.PENDING
        self.phase = ReviewPhase.INIT
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        # Progress tracking
        self.total_files = 0
        self.processed_files = 0
        self.current_files: List[str] = []  # Currently processing files

        # File grouping
        self.file_groups: Dict[str, List[str]] = {}

        # Results
        self.results: List[Dict] = []
        self.errors: List[Dict] = []

        # Multi-round analysis tracking
        self.multi_round_files: Dict[str, int] = {}  # file -> round count
        self.context_files: Dict[str, List[str]] = {}  # file -> related files loaded

        # Cancellation
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        self.status = TaskStatus.CANCELLED

    def is_cancelled(self):
        return self._cancelled

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "phase": self.phase.value,
            "progress": {
                "total_files": self.total_files,
                "processed_files": self.processed_files,
                "current_files": self.current_files,
                "percentage": int((self.processed_files / self.total_files * 100) if self.total_files > 0 else 0)
            },
            "file_groups": self.file_groups,
            "results_count": len(self.results),
            "errors_count": len(self.errors),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, ReviewTask] = {}

    def create_task(self, project_id: int, base_branch: str, target_branch: str, scope: str, specific_files: Optional[List[str]] = None) -> ReviewTask:
        task_id = str(uuid.uuid4())
        task = ReviewTask(task_id, project_id, base_branch, target_branch, scope, specific_files)
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[ReviewTask]:
        return self.tasks.get(task_id)

    def remove_task(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tasks older than max_age_hours"""
        now = datetime.now()
        to_remove = []
        for task_id, task in self.tasks.items():
            age = (now - task.created_at).total_seconds() / 3600
            if age > max_age_hours and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.tasks[task_id]

task_manager = TaskManager()
