from typing import List, Dict, Set
import os
import re

class FileGrouper:
    """智能文件分组器，根据文件路径和依赖关系分组"""

    @staticmethod
    def group_files(files: List[Dict]) -> Dict[str, List[str]]:
        """
        将文件分组以便更好地进行关联分析

        返回格式:
        {
            "models": ["user.py", "order.py"],
            "services": ["user_service.py"],
            "apis": ["api.py"],
            "utils": ["helpers.py"],
            "related_groups": {
                "group_1": ["api.py", "service.py", "model.py"]
            }
        }
        """
        groups = {
            "models": [],
            "services": [],
            "apis": [],
            "controllers": [],
            "views": [],
            "utils": [],
            "config": [],
            "tests": [],
            "other": []
        }

        # 按路径模式分类
        for file_info in files:
            path = file_info['path'].lower()

            if 'model' in path or 'entity' in path or 'schema' in path:
                groups["models"].append(file_info['path'])
            elif 'service' in path or 'business' in path:
                groups["services"].append(file_info['path'])
            elif 'api' in path or 'endpoint' in path or 'route' in path:
                groups["apis"].append(file_info['path'])
            elif 'controller' in path:
                groups["controllers"].append(file_info['path'])
            elif 'view' in path or 'template' in path:
                groups["views"].append(file_info['path'])
            elif 'util' in path or 'helper' in path or 'tool' in path:
                groups["utils"].append(file_info['path'])
            elif 'config' in path or 'setting' in path:
                groups["config"].append(file_info['path'])
            elif 'test' in path or 'spec' in path:
                groups["tests"].append(file_info['path'])
            else:
                groups["other"].append(file_info['path'])

        # 移除空分组
        groups = {k: v for k, v in groups.items() if v}

        return groups

    @staticmethod
    def find_related_files(file_path: str, all_files: List[str]) -> List[str]:
        """
        根据文件名找到可能相关的文件
        例如: user_service.py -> [user.py, user_model.py, user_api.py]
        """
        related = []
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        # 移除常见后缀
        for suffix in ['_service', '_api', '_controller', '_model', '_view', '_test']:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break

        # 查找包含相同基础名的文件
        for other_file in all_files:
            if other_file == file_path:
                continue
            other_base = os.path.splitext(os.path.basename(other_file))[0]
            if base_name in other_base or other_base in base_name:
                related.append(other_file)

        return related

    @staticmethod
    def parse_imports(file_content: str, file_path: str) -> List[str]:
        """
        解析文件中的import语句，返回导入的模块列表
        支持Python和JavaScript
        """
        imports = []

        # Python imports
        python_patterns = [
            r'from\s+([.\w]+)\s+import',
            r'import\s+([.\w]+)',
        ]

        # JavaScript/TypeScript imports
        js_patterns = [
            r'import\s+.*\s+from\s+[\'"](.+)[\'"]',
            r'require\([\'"](.+)[\'"]\)',
        ]

        patterns = python_patterns if file_path.endswith('.py') else js_patterns

        for pattern in patterns:
            matches = re.findall(pattern, file_content)
            imports.extend(matches)

        return imports

    @staticmethod
    def build_dependency_graph(files: List[Dict], repo_path: str) -> Dict[str, List[str]]:
        """
        构建文件依赖关系图
        返回: {file_path: [依赖的文件列表]}
        """
        dependency_graph = {}

        for file_info in files:
            file_path = file_info['path']
            full_path = os.path.join(repo_path, file_path)

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    imports = FileGrouper.parse_imports(content, file_path)

                    # 将import转换为实际文件路径
                    dependencies = []
                    for imp in imports:
                        # 简化处理：查找包含该模块名的文件
                        for other_file in files:
                            if imp.replace('.', '/') in other_file['path']:
                                dependencies.append(other_file['path'])

                    dependency_graph[file_path] = dependencies
            except Exception:
                dependency_graph[file_path] = []

        return dependency_graph
