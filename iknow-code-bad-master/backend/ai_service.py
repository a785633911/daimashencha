import httpx
import json
from typing import List, Dict, AsyncIterator, Callable, Optional
import os

class AIService:
    def __init__(self, api_url: str, api_key: str, model: str, stream_enabled: bool = False):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.stream_enabled = stream_enabled

    async def review_code(self, code: str, file_path: str, workflow: str, format_constraint: str, standards: str,
                         stream_callback: Optional[Callable] = None) -> Dict:
        prompt = f"""你是一个专业的代码审查助手。

工作流程：
{workflow}

回答格式约束：
{format_constraint}

审查标准：
{standards}

严重程度评级标准（必须严格遵守）：
- 致命：代码错误，比如缺少标点、写法错误、标点错误、结构不完整、括号不匹配等会导致系统无法运行的问题
- 高：逻辑错误
- 中：一些小问题，不影响使用，但是从长期来看，可能会存在维护困难，出现一个BUG的问题；代码重复；逻辑不完善
- 低：一些小问题，不影响使用，但是从长期来看，可能会存在维护困难，但是不会出现BUG；存在冗余代码；注释和代码不匹配
- 建议：无错误，无逻辑问题，但是能提高性能，规范代码相关的建议，是否采纳都对系统无任何影响

请审查以下代码文件：
文件路径：{file_path}

代码内容：
```
{code}
```

请严格按照工作流程、回答格式约束和审查标准进行审查。"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": self.stream_enabled
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            if self.stream_enabled and stream_callback:
                # 流式输出
                full_content = ""
                async with client.stream("POST", f"{self.api_url}/chat/completions", headers=headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_content += content
                                        await stream_callback(content)
                            except json.JSONDecodeError:
                                continue
                return {"content": full_content}
            else:
                # 非流式输出
                response = await client.post(f"{self.api_url}/chat/completions", headers=headers, json=payload)
                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    return {"content": result["choices"][0]["message"]["content"]}
                return {"content": "审查失败"}

    def load_documents(self, paths: List[str]) -> str:
        content = ""
        for path in paths:
            if os.path.exists(path):
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content += f.read() + "\n\n"
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.md'):
                                file_path = os.path.join(root, file)
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content += f.read() + "\n\n"
        return content

    def parse_review_result(self, content: str) -> List[Dict]:
        issues = []
        lines = content.split('\n')

        current_issue = {}
        for line in lines:
            line = line.strip()
            if line.startswith('问题类型：'):
                if current_issue:
                    issues.append(current_issue)
                current_issue = {'issue_type': line.replace('问题类型：', '').strip()}
            elif line.startswith('严重程度：'):
                current_issue['severity'] = line.replace('严重程度：', '').strip()
            elif line.startswith('文件路径：'):
                current_issue['file_path'] = line.replace('文件路径：', '').strip()
            elif line.startswith('行号：'):
                line_num = line.replace('行号：', '').strip()
                if '-' in line_num:
                    start, end = line_num.split('-')
                    current_issue['line_start'] = int(start)
                    current_issue['line_end'] = int(end)
                else:
                    current_issue['line_start'] = int(line_num)
                    current_issue['line_end'] = int(line_num)
            elif line.startswith('问题描述：'):
                current_issue['description'] = line.replace('问题描述：', '').strip()

        if current_issue:
            issues.append(current_issue)

        return issues

    async def review_with_context(self, main_file: str, main_code: str, context_files: Dict[str, str],
                                  workflow: str, format_constraint: str, standards: str,
                                  previous_issues: List[Dict], stream_callback: Optional[Callable] = None) -> Dict:
        """
        多轮分析：带上下文的代码审查

        Args:
            main_file: 主要审查的文件路径
            main_code: 主要文件的代码
            context_files: 相关文件 {file_path: code_content}
            previous_issues: 第一轮发现的问题
        """
        context_info = "\n\n".join([
            f"相关文件: {path}\n```\n{code}\n```"
            for path, code in context_files.items()
        ])

        issues_info = "\n".join([
            f"- {issue.get('issue_type', '未知')}: {issue.get('description', '')}"
            for issue in previous_issues
        ])

        prompt = f"""你是一个专业的代码审查助手，正在进行第二轮深度分析。

工作流程：
{workflow}

回答格式约束：
{format_constraint}

审查标准：
{standards}

严重程度评级标准（必须严格遵守）：
- 致命：代码错误，比如缺少标点、写法错误、标点错误、结构不完整、括号不匹配等会导致系统无法运行的问题
- 高：逻辑错误
- 中：一些小问题，不影响使用，但是从长期来看，可能会存在维护困难，出现一个BUG的问题；代码重复；逻辑不完善
- 低：一些小问题，不影响使用，但是从长期来看，可能会存在维护困难，但是不会出现BUG；存在冗余代码；注释和代码不匹配
- 建议：无错误，无逻辑问题，但是能提高性能，规范代码相关的建议，是否采纳都对系统无任何影响

第一轮审查发现了以下问题：
{issues_info}

现在请结合相关文件进行深度分析：

主要文件: {main_file}
```
{main_code}
```

{context_info}

请重点关注：
1. 跨文件的逻辑一致性
2. 接口调用的正确性
3. 数据流转的完整性
4. 潜在的架构问题

请严格按照回答格式约束输出结果。"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": self.stream_enabled
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            if self.stream_enabled and stream_callback:
                full_content = ""
                async with client.stream("POST", f"{self.api_url}/chat/completions", headers=headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_content += content
                                        await stream_callback(content)
                            except json.JSONDecodeError:
                                continue
                return {"content": full_content}
            else:
                response = await client.post(f"{self.api_url}/chat/completions", headers=headers, json=payload)
                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    return {"content": result["choices"][0]["message"]["content"]}
                return {"content": "深度分析失败"}

    async def analyze_impact(self, issue: Dict, all_files: Dict[str, str],
                            stream_callback: Optional[Callable] = None) -> Dict:
        """
        影响范围分析：分析某个问题对其他文件的影响
        """
        files_info = "\n\n".join([
            f"文件: {path}\n```\n{code[:500]}...\n```"  # 只取前500字符
            for path, code in list(all_files.items())[:10]  # 最多分析10个文件
        ])

        prompt = f"""你是一个专业的代码审查助手，正在进行影响范围分析。

发现的问题：
类型: {issue.get('issue_type', '未知')}
文件: {issue.get('file_path', '未知')}
描述: {issue.get('description', '')}

请分析这个问题可能影响到的其他文件：

{files_info}

请列出：
1. 受影响的文件列表
2. 影响的具体位置（行号）
3. 影响的原因

输出格式：
影响文件：文件路径
影响位置：行号
影响原因：简要说明
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": self.stream_enabled
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            if self.stream_enabled and stream_callback:
                full_content = ""
                async with client.stream("POST", f"{self.api_url}/chat/completions", headers=headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_content += content
                                        await stream_callback(content)
                            except json.JSONDecodeError:
                                continue
                return {"content": full_content}
            else:
                response = await client.post(f"{self.api_url}/chat/completions", headers=headers, json=payload)
                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    return {"content": result["choices"][0]["message"]["content"]}
                return {"content": "影响分析失败"}
