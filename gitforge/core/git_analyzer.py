"""
Git Analyzer - Analyze git repository state and extract diffs.
Git仓库分析器 - 提取diff、提交历史等信息。
"""

import os
import re
import subprocess
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GitDiff:
    """Represents a git diff for a file."""
    file_path: str
    change_type: str  # added, modified, deleted, renamed
    additions: int
    deletions: int
    diff_content: str
    is_binary: bool = False


@dataclass
class GitCommit:
    """Represents a git commit."""
    hash: str
    short_hash: str
    message: str
    author: str
    date: str
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


class GitAnalyzer:
    """
    Analyze git repository and extract useful information.
    Requires git to be installed and repository to be initialized.
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self._git_available = self._check_git()

    def _check_git(self) -> bool:
        """Check if git is available and this is a git repository."""
        try:
            result = self._run_git(["rev-parse", "--git-dir"])
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _run_git(self, args: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git"] + args
        return subprocess.run(
            cmd,
            cwd=cwd or self.repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        return self._git_available

    def get_staged_diff(self) -> List[GitDiff]:
        """Get diff of staged changes."""
        if not self._git_available:
            return []

        result = self._run_git(["diff", "--cached", "--stat"])
        if result.returncode != 0 or not result.stdout.strip():
            return []

        # Get full diff
        diff_result = self._run_git(["diff", "--cached"])
        if diff_result.returncode != 0:
            return []

        return self._parse_diff(diff_result.stdout)

    def get_unstaged_diff(self) -> List[GitDiff]:
        """Get diff of unstaged changes."""
        if not self._git_available:
            return []

        diff_result = self._run_git(["diff"])
        if diff_result.returncode != 0:
            return []

        return self._parse_diff(diff_result.stdout)

    def get_last_commit_diff(self) -> List[GitDiff]:
        """Get diff of the last commit."""
        if not self._git_available:
            return []

        diff_result = self._run_git(["diff", "HEAD~1", "HEAD"])
        if diff_result.returncode != 0:
            return []

        return self._parse_diff(diff_result.stdout)

    def _parse_diff(self, diff_text: str) -> List[GitDiff]:
        """Parse git diff text into GitDiff objects."""
        diffs = []
        if not diff_text.strip():
            return diffs

        # Split by file diff
        file_pattern = r'^diff --git a/(.+?) b/(.+?)$'
        files = re.split(file_pattern, diff_text, flags=re.MULTILINE)

        if len(files) < 4:
            # No files found, might be a single file diff
            return diffs

        # files[0] is preamble, then triplets of [file_a, file_b, content]
        for i in range(1, len(files), 3):
            if i + 2 >= len(files):
                break

            file_a = files[i]
            file_b = files[i + 1]
            content = files[i + 2]

            # Determine change type
            change_type = "modified"
            if file_a == "/dev/null":
                change_type = "added"
            elif file_b == "/dev/null":
                change_type = "deleted"
            elif file_a != file_b:
                change_type = "renamed"

            # Check if binary
            is_binary = "Binary files" in content or "\x00" in content[:1000]

            # Count additions/deletions
            additions = content.count("\n+") - content.count("\n+++")
            deletions = content.count("\n-") - content.count("\n---")
            additions = max(0, additions)
            deletions = max(0, deletions)

            diffs.append(GitDiff(
                file_path=file_b if file_b != "/dev/null" else file_a,
                change_type=change_type,
                additions=additions,
                deletions=deletions,
                diff_content=content.strip(),
                is_binary=is_binary,
            ))

        return diffs

    def get_commit_history(
        self,
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_count: int = 50,
    ) -> List[GitCommit]:
        """Get commit history."""
        if not self._git_available:
            return []

        args = [
            "log",
            f"--max-count={max_count}",
            "--pretty=format:%H|%h|%s|%an|%ad|%d",
            "--date=short",
            "--numstat",
        ]

        if since:
            args.extend(["--since", since])
        if until:
            args.extend(["--until", until])

        result = self._run_git(args)
        if result.returncode != 0:
            return []

        return self._parse_log(result.stdout)

    def _parse_log(self, log_text: str) -> List[GitCommit]:
        """Parse git log output."""
        commits = []
        lines = log_text.strip().split("\n")

        current_commit = None
        files_changed = 0
        insertions = 0
        deletions = 0

        for line in lines:
            if "|" in line and not line.startswith(" "):
                # Commit line
                if current_commit:
                    current_commit.files_changed = files_changed
                    current_commit.insertions = insertions
                    current_commit.deletions = deletions
                    commits.append(current_commit)

                parts = line.split("|")
                if len(parts) >= 5:
                    current_commit = GitCommit(
                        hash=parts[0],
                        short_hash=parts[1],
                        message=parts[2],
                        author=parts[3],
                        date=parts[4],
                        files_changed=0,
                        insertions=0,
                        deletions=0,
                    )
                    files_changed = 0
                    insertions = 0
                    deletions = 0
            elif "\t" in line:
                # Numstat line
                parts = line.split("\t")
                if len(parts) >= 3:
                    files_changed += 1
                    if parts[0] != "-":
                        insertions += int(parts[0])
                    if parts[1] != "-":
                        deletions += int(parts[1])

        # Don't forget the last commit
        if current_commit:
            current_commit.files_changed = files_changed
            current_commit.insertions = insertions
            current_commit.deletions = deletions
            commits.append(current_commit)

        return commits

    def get_repo_info(self) -> Dict[str, Any]:
        """Get repository information."""
        if not self._git_available:
            return {"is_git_repo": False}

        info = {"is_git_repo": True}

        # Remote URL
        remote_result = self._run_git(["remote", "get-url", "origin"])
        if remote_result.returncode == 0:
            info["remote_url"] = remote_result.stdout.strip()

        # Branch
        branch_result = self._run_git(["branch", "--show-current"])
        if branch_result.returncode == 0:
            info["current_branch"] = branch_result.stdout.strip()

        # Total commits
        count_result = self._run_git(["rev-list", "--count", "HEAD"])
        if count_result.returncode == 0:
            info["total_commits"] = int(count_result.stdout.strip())

        # Last tag
        tag_result = self._run_git(["describe", "--tags", "--abbrev=0"])
        if tag_result.returncode == 0:
            info["last_tag"] = tag_result.stdout.strip()

        return info

    def stage_files(self, files: Optional[List[str]] = None) -> bool:
        """Stage files for commit."""
        if not self._git_available:
            return False

        if files:
            result = self._run_git(["add"] + files)
        else:
            result = self._run_git(["add", "."])

        return result.returncode == 0

    def commit(self, message: str, allow_empty: bool = False) -> bool:
        """Create a commit with the given message."""
        if not self._git_available:
            return False

        args = ["commit", "-m", message]
        if allow_empty:
            args.append("--allow-empty")

        result = self._run_git(args)
        return result.returncode == 0

    def has_staged_changes(self) -> bool:
        """Check if there are staged changes."""
        if not self._git_available:
            return False

        result = self._run_git(["diff", "--cached", "--quiet"])
        return result.returncode != 0

    def has_unstaged_changes(self) -> bool:
        """Check if there are unstaged changes."""
        if not self._git_available:
            return False

        result = self._run_git(["diff", "--quiet"])
        return result.returncode != 0

    def get_changed_files(self, staged: bool = True) -> List[str]:
        """Get list of changed files."""
        if not self._git_available:
            return []

        cmd = ["diff", "--cached", "--name-only"] if staged else ["diff", "--name-only"]
        result = self._run_git(cmd)

        if result.returncode == 0:
            return [f for f in result.stdout.strip().split("\n") if f]
        return []
