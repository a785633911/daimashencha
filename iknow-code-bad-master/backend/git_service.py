import git
from typing import List, Dict
import os

class GitService:
    @staticmethod
    def get_branches(repo_path: str) -> List[str]:
        try:
            repo = git.Repo(repo_path)
            return [ref.name.replace('origin/', '') for ref in repo.refs if 'origin/' in ref.name]
        except:
            return []

    @staticmethod
    def get_changed_files(repo_path: str, base_branch: str, target_branch: str, scope: str = "all") -> List[Dict]:
        try:
            repo = git.Repo(repo_path)

            # Fetch latest from remote
            try:
                repo.remotes.origin.fetch()
            except:
                pass

            # Resolve base branch reference
            base_ref = base_branch
            if '/' not in base_branch:
                try:
                    repo.commit(f'origin/{base_branch}')
                    base_ref = f'origin/{base_branch}'
                except:
                    try:
                        repo.commit(base_branch)
                        base_ref = base_branch
                    except:
                        base_ref = f'origin/{base_branch}'

            files = []

            if scope in ["committed", "committed+staged", "all"]:
                diff_index = repo.commit(base_ref).diff(repo.commit(target_branch))
                for diff_item in diff_index:
                    status = "modified"
                    if diff_item.change_type == 'A':
                        status = "added"
                    elif diff_item.change_type == 'D':
                        status = "deleted"
                    elif diff_item.change_type == 'R':
                        status = "renamed"
                    path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                    files.append({"path": path, "status": status})

            if scope in ["staged", "committed+staged", "staged+unstaged", "all"]:
                staged_diff = repo.index.diff("HEAD")
                for diff_item in staged_diff:
                    path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                    if not any(f["path"] == path for f in files):
                        files.append({"path": path, "status": "modified"})

            if scope in ["unstaged", "staged+unstaged", "all"]:
                unstaged_diff = repo.index.diff(None)
                for diff_item in unstaged_diff:
                    path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                    if not any(f["path"] == path for f in files):
                        files.append({"path": path, "status": "modified"})

            return files
        except Exception as e:
            return []

    @staticmethod
    def get_file_content(repo_path: str, file_path: str) -> str:
        try:
            full_path = os.path.join(repo_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""

    @staticmethod
    def get_current_branch(repo_path: str) -> str:
        try:
            repo = git.Repo(repo_path)
            return repo.active_branch.name
        except:
            return ""

    @staticmethod
    def get_remote_branches(repo_path: str) -> List[str]:
        try:
            repo = git.Repo(repo_path)
            # Fetch latest from remote
            try:
                repo.remotes.origin.fetch()
            except:
                pass
            # Get all remote branches
            remote_refs = [ref.name.replace('origin/', '') for ref in repo.remotes.origin.refs if ref.name != 'origin/HEAD']
            return remote_refs
        except:
            return []

    @staticmethod
    def get_git_status(repo_path: str, branch: str, base_branch: str) -> Dict:
        try:
            repo = git.Repo(repo_path)

            # Fetch latest from remote to ensure we have up-to-date refs
            try:
                repo.remotes.origin.fetch()
            except:
                pass

            # Get commits ahead of base branch
            try:
                # Determine the correct base branch reference
                base_ref = base_branch
                if '/' not in base_branch:
                    # Try origin/ prefix for remote branches
                    try:
                        repo.commit(f'origin/{base_branch}')
                        base_ref = f'origin/{base_branch}'
                    except:
                        try:
                            repo.commit(base_branch)
                            base_ref = base_branch
                        except:
                            base_ref = f'origin/{base_branch}'
                else:
                    base_ref = base_branch

                commits_ahead = list(repo.iter_commits(f'{base_ref}..{branch}'))
                staged_commits = len(commits_ahead)
            except Exception as e:
                staged_commits = 0

            # Get file changes - including committed, staged, and unstaged
            try:
                # Determine the correct base branch reference
                base_ref = base_branch
                if '/' not in base_branch:
                    try:
                        repo.commit(f'origin/{base_branch}')
                        base_ref = f'origin/{base_branch}'
                    except:
                        try:
                            repo.commit(base_branch)
                            base_ref = base_branch
                        except:
                            base_ref = f'origin/{base_branch}'
                else:
                    base_ref = base_branch

                # Track all changed files to avoid duplicates
                changed_files = {}

                # 1. Get diff between base branch and current branch (committed changes)
                diff_index = repo.commit(base_ref).diff(repo.commit(branch))
                for diff_item in diff_index:
                    path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                    changed_files[path] = diff_item.change_type

                # 2. Get staged changes
                staged_diff = repo.index.diff("HEAD")
                for diff_item in staged_diff:
                    path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                    if path not in changed_files:
                        changed_files[path] = diff_item.change_type

                # 3. Get unstaged changes
                unstaged_diff = repo.index.diff(None)
                for diff_item in unstaged_diff:
                    path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                    if path not in changed_files:
                        changed_files[path] = diff_item.change_type

                # Count by change type
                modified_files = 0
                added_files = 0
                deleted_files = 0

                for path, change_type in changed_files.items():
                    if change_type == 'M':  # Modified
                        modified_files += 1
                    elif change_type == 'A':  # Added
                        added_files += 1
                    elif change_type == 'D':  # Deleted
                        deleted_files += 1
                    elif change_type == 'R':  # Renamed (count as modified)
                        modified_files += 1

            except Exception as e:
                modified_files = 0
                added_files = 0
                deleted_files = 0

            return {
                "staged_commits": staged_commits,
                "modified_files": modified_files,
                "added_files": added_files,
                "deleted_files": deleted_files
            }
        except Exception as e:
            return {
                "staged_commits": 0,
                "modified_files": 0,
                "added_files": 0,
                "deleted_files": 0
            }
