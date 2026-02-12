import asyncio
from typing import Dict, List
from datetime import datetime
from websocket_manager import manager
from task_manager import task_manager, TaskStatus, ReviewPhase
from file_grouper import FileGrouper
from ai_service import AIService
from git_service import GitService
import database

class ReviewProcessor:
    """WebSocket审查处理器 - 核心业务逻辑"""

    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent

    async def process_review(self, task_id: str, project, config, db):
        """
        执行完整的审查流程
        """
        task = task_manager.get_task(task_id)
        if not task:
            return

        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            # 初始化AI服务
            ai_service = AIService(
                config.api_url,
                config.api_key,
                config.review_model,
                config.stream_enabled
            )

            # 阶段1: 初始化
            await self._phase_init(task, project, config, ai_service)

            if task.is_cancelled():
                return

            # 阶段2: 文件分组
            await self._phase_file_grouping(task, project)

            if task.is_cancelled():
                return

            # 阶段3: 快速扫描
            await self._phase_quick_scan(task, project, ai_service, config)

            if task.is_cancelled():
                return

            # 阶段4: 深度分析（针对需要多轮分析的文件）
            await self._phase_deep_analysis(task, project, ai_service, config)

            if task.is_cancelled():
                return

            # 阶段5: 生成报告
            await self._phase_generate_report(task, db, project)

            # 完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.phase = ReviewPhase.COMPLETE

            await manager.send_to_task(task_id, {
                "type": "complete",
                "summary": {
                    "total_files": task.total_files,
                    "processed_files": task.processed_files,
                    "total_issues": len(task.results),
                    "errors": len(task.errors)
                }
            })

        except Exception as e:
            task.status = TaskStatus.FAILED
            await manager.send_to_task(task_id, {
                "type": "error",
                "message": f"审查失败: {str(e)}"
            })

    async def _phase_init(self, task, project, config, ai_service):
        """阶段1: 初始化"""
        task.phase = ReviewPhase.INIT

        await manager.send_to_task(task.task_id, {
            "type": "phase_change",
            "phase": "init",
            "message": "初始化审查环境..."
        })

        # 加载文档
        workflow_docs = config.workflow_paths or []
        format_docs = config.format_paths or []
        standard_docs = config.standard_paths or []

        workflow = ai_service.load_documents(workflow_docs)
        format_constraint = ai_service.load_documents(format_docs)
        standards = ai_service.load_documents(standard_docs)

        # 发送初始化详情
        await manager.send_to_task(task.task_id, {
            "type": "progress",
            "step": "init",
            "message": "环境初始化完成",
            "details": {
                "project_name": project.name,
                "project_path": project.path,
                "ai_config": config.name,
                "review_model": config.review_model,
                "workflow_loaded": len(workflow) > 0,
                "format_loaded": len(format_constraint) > 0,
                "standards_loaded": len(standards) > 0,
                "workflow_docs": workflow_docs,
                "format_docs": format_docs,
                "standard_docs": standard_docs
            }
        })

        # 存储到task中供后续使用
        task.workflow = workflow
        task.format_constraint = format_constraint
        task.standards = standards

    async def _phase_file_grouping(self, task, project):
        """阶段2: 文件分组"""
        task.phase = ReviewPhase.FILE_GROUPING

        await manager.send_to_task(task.task_id, {
            "type": "phase_change",
            "phase": "file_grouping",
            "message": "分析文件结构..."
        })

        # 获取变更文件
        changed_files = GitService.get_changed_files(
            project.path,
            task.base_branch,
            task.target_branch,
            task.scope
        )

        # 如果指定了特定文件，只处理这些文件
        if task.specific_files:
            changed_files = [f for f in changed_files if f['path'] in task.specific_files]

        task.total_files = len(changed_files)
        task.changed_files = changed_files

        # 文件分组
        file_groups = FileGrouper.group_files(changed_files)
        task.file_groups = file_groups

        await manager.send_to_task(task.task_id, {
            "type": "file_grouping",
            "groups": file_groups,
            "total_files": task.total_files
        })

    async def _phase_quick_scan(self, task, project, ai_service, config):
        """阶段3: 快速扫描（并行处理）"""
        task.phase = ReviewPhase.QUICK_SCAN

        await manager.send_to_task(task.task_id, {
            "type": "phase_change",
            "phase": "quick_scan",
            "message": f"开始快速扫描 ({task.total_files} 个文件)..."
        })

        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_file(file_info):
            async with semaphore:
                if task.is_cancelled():
                    return

                file_path = file_info['path']

                # 发送文件开始消息
                await manager.send_to_task(task.task_id, {
                    "type": "file_start",
                    "file": file_path,
                    "index": task.processed_files + 1,
                    "total": task.total_files
                })

                task.current_files.append(file_path)

                try:
                    # 读取文件内容
                    code = GitService.get_file_content(project.path, file_path)

                    if not code:
                        await manager.send_to_task(task.task_id, {
                            "type": "file_complete",
                            "file": file_path,
                            "status": "skipped",
                            "message": "文件内容为空"
                        })
                        task.current_files.remove(file_path)
                        task.processed_files += 1
                        return

                    # 流式回调
                    async def stream_callback(content):
                        await manager.send_to_task(task.task_id, {
                            "type": "ai_stream",
                            "file": file_path,
                            "content": content,
                            "round": 1
                        })

                    # AI审查
                    start_time = datetime.now()
                    result = await ai_service.review_code(
                        code,
                        file_path,
                        task.workflow,
                        task.format_constraint,
                        task.standards,
                        stream_callback if config.stream_enabled else None
                    )
                    duration = (datetime.now() - start_time).total_seconds()

                    # 解析结果
                    issues = ai_service.parse_review_result(result['content'])

                    # 添加文件路径到每个问题
                    for issue in issues:
                        if 'file_path' not in issue or not issue['file_path']:
                            issue['file_path'] = file_path

                    task.results.extend(issues)

                    # 发送文件完成消息
                    await manager.send_to_task(task.task_id, {
                        "type": "file_complete",
                        "file": file_path,
                        "status": "success",
                        "issues_found": len(issues),
                        "issues": issues,
                        "duration": duration
                    })

                    # 检查是否需要深度分析
                    if len(issues) > 0 and self._needs_deep_analysis(issues):
                        task.multi_round_files[file_path] = 1  # 标记需要第2轮

                except Exception as e:
                    task.errors.append({
                        "file": file_path,
                        "error": str(e)
                    })

                    await manager.send_to_task(task.task_id, {
                        "type": "file_error",
                        "file": file_path,
                        "error": str(e)
                    })

                finally:
                    if file_path in task.current_files:
                        task.current_files.remove(file_path)
                    task.processed_files += 1

                    # 发送进度更新
                    await manager.send_to_task(task.task_id, {
                        "type": "progress_update",
                        "processed": task.processed_files,
                        "total": task.total_files,
                        "percentage": int(task.processed_files / task.total_files * 100)
                    })

        # 并行处理所有文件
        tasks_list = [process_file(f) for f in task.changed_files]
        await asyncio.gather(*tasks_list)

    async def _phase_deep_analysis(self, task, project, ai_service, config):
        """阶段4: 深度分析（多轮对话）"""
        if not task.multi_round_files:
            return  # 没有需要深度分析的文件

        task.phase = ReviewPhase.DEEP_ANALYSIS

        await manager.send_to_task(task.task_id, {
            "type": "phase_change",
            "phase": "deep_analysis",
            "message": f"开始深度分析 ({len(task.multi_round_files)} 个文件需要进一步分析)..."
        })

        for file_path, round_count in task.multi_round_files.items():
            if task.is_cancelled():
                break

            await manager.send_to_task(task.task_id, {
                "type": "multi_round_start",
                "file": file_path,
                "round": 2,
                "reason": "发现需要跨文件分析的问题"
            })

            # 查找相关文件
            all_file_paths = [f['path'] for f in task.changed_files]
            related_files = FileGrouper.find_related_files(file_path, all_file_paths)

            if related_files:
                # 加载相关文件内容
                context_files = {}
                for related_path in related_files[:3]:  # 最多加载3个相关文件
                    content = GitService.get_file_content(project.path, related_path)
                    if content:
                        context_files[related_path] = content

                task.context_files[file_path] = list(context_files.keys())

                await manager.send_to_task(task.task_id, {
                    "type": "context_loading",
                    "current_file": file_path,
                    "loading_files": list(context_files.keys()),
                    "reason": "进行跨文件关联分析"
                })

                # 获取该文件的第一轮问题
                first_round_issues = [
                    issue for issue in task.results
                    if issue.get('file_path') == file_path
                ]

                # 流式回调
                async def stream_callback(content):
                    await manager.send_to_task(task.task_id, {
                        "type": "ai_thinking",
                        "file": file_path,
                        "round": 2,
                        "thought": content,
                        "context_files": list(context_files.keys())
                    })

                # 第二轮分析
                main_code = GitService.get_file_content(project.path, file_path)
                result = await ai_service.review_with_context(
                    file_path,
                    main_code,
                    context_files,
                    task.workflow,
                    task.format_constraint,
                    task.standards,
                    first_round_issues,
                    stream_callback if config.stream_enabled else None
                )

                # 解析新发现的问题
                new_issues = ai_service.parse_review_result(result['content'])
                for issue in new_issues:
                    issue['analysis_round'] = 2
                    issue['context_files'] = list(context_files.keys())

                task.results.extend(new_issues)

                await manager.send_to_task(task.task_id, {
                    "type": "deep_analysis_complete",
                    "file": file_path,
                    "new_issues_found": len(new_issues),
                    "issues": new_issues
                })

    async def _phase_generate_report(self, task, db, project):
        """阶段5: 生成报告"""
        task.phase = ReviewPhase.GENERATING_REPORT

        await manager.send_to_task(task.task_id, {
            "type": "phase_change",
            "phase": "generating_report",
            "message": "生成审查报告..."
        })

        # 保存审查记录到数据库
        record = database.ReviewRecord(
            project_id=project.id,
            branch=task.target_branch,
            base_branch=task.base_branch,
            review_scope=task.scope,
            file_count=task.total_files,
            issue_count=len(task.results)
        )
        db.add(record)
        db.commit()

        await manager.send_to_task(task.task_id, {
            "type": "report_generated",
            "record_id": record.id
        })

    def _needs_deep_analysis(self, issues: List[Dict]) -> bool:
        """
        判断是否需要深度分析
        规则：如果发现高严重度问题，或者问题描述中包含特定关键词
        """
        keywords = ['调用', '依赖', '接口', '事务', '一致性', '关联']

        for issue in issues:
            # 高严重度问题
            if issue.get('severity') == '高':
                return True

            # 包含关键词
            description = issue.get('description', '')
            if any(keyword in description for keyword in keywords):
                return True

        return False

review_processor = ReviewProcessor(max_concurrent=3)
