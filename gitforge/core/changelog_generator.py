"""
Changelog Generator - AI-powered CHANGELOG.md generation from commit history.
AI驱动的CHANGELOG生成器 - 基于提交历史自动生成更新日志。
"""

import os
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from .git_analyzer import GitAnalyzer, GitCommit
from .llm_client import GLMClient


class ChangelogGenerator:
    """
    Generate CHANGELOG.md from git commit history using AI.
    Follows Keep a Changelog format.
    """

    SYSTEM_PROMPT = """You are GitForge, an expert changelog writer.
Generate a professional CHANGELOG entry from the provided git commits.

Format (Keep a Changelog):
## [Version] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements

Rules:
1. Group commits by type (feat→Added, fix→Fixed, refactor→Changed, etc.)
2. Write from user's perspective, not developer's
3. Be specific about what changed and why it matters
4. Include issue references when available
5. Language: Match user's preferred language

Output ONLY the changelog content, no explanations."""

    def __init__(self, llm_client: Optional[GLMClient] = None):
        self.llm_client = llm_client or GLMClient()
        self.git = GitAnalyzer()

    def generate(
        self,
        since_tag: Optional[str] = None,
        until_tag: Optional[str] = None,
        version: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Generate changelog from commits.
        
        Returns dict with:
        - changelog: Generated changelog text
        - commits_count: Number of commits processed
        - version: Version string
        """
        # Get commits
        if since_tag:
            commits = self._get_commits_since_tag(since_tag)
        else:
            commits = self.git.get_commit_history(max_count=50)

        if not commits:
            # Return mock response for testing
            mock_changelog = (
                "🤖 [Mock Mode] This is a simulated changelog.\n\n"
                "To get real AI-generated changelogs, please set your GLM API key:\n"
                "  export GLM_API_KEY='your-api-key'\n\n"
                f"Version: {version or 'Unreleased'}\n"
                "No commits found in the specified range."
            )
            return {
                "changelog": mock_changelog,
                "commits_count": 0,
                "version": version or "Unreleased",
                "error": "No commits found in the specified range.",
            }

        # Format commits for prompt
        commits_text = self._format_commits(commits)

        # Build prompt
        version_str = version or "Unreleased"
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        lang_instruction = ""
        if language == "zh":
            lang_instruction = "\nPlease generate the changelog in Chinese (中文)."
        elif language == "zh-tw":
            lang_instruction = "\nPlease generate the changelog in Traditional Chinese (繁體中文)."

        prompt = f"""Generate a changelog entry for version {version_str} ({date_str}).

Commits since last release:
{commits_text}

{lang_instruction}
"""

        # Generate with LLM
        response = self.llm_client.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=4096,
        )

        return {
            "changelog": response.strip(),
            "commits_count": len(commits),
            "version": version_str,
        }

    def generate_full(
        self,
        output_path: str = "CHANGELOG.md",
        language: str = "en",
    ) -> Dict[str, Any]:
        """Generate or update full CHANGELOG.md file."""
        # Get all tags
        tags = self._get_tags()
        
        changelog_sections = []
        
        if not tags:
            # No tags, generate from recent commits
            result = self.generate(version="Unreleased", language=language)
            changelog_sections.append(result["changelog"])
        else:
            # Generate for each tag range
            for i, tag in enumerate(tags):
                since_tag = tags[i + 1] if i + 1 < len(tags) else None
                result = self.generate(
                    since_tag=since_tag,
                    until_tag=tag,
                    version=tag,
                    language=language,
                )
                if result["changelog"]:
                    changelog_sections.append(result["changelog"])

        # Build full changelog
        header = self._get_changelog_header(language)
        full_changelog = header + "\n\n" + "\n\n".join(changelog_sections)

        # Write to file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_changelog)
            return {
                "success": True,
                "path": output_path,
                "sections": len(changelog_sections),
            }
        except IOError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def update(
        self,
        output_path: str = "CHANGELOG.md",
        version: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Update existing CHANGELOG.md with new entries."""
        # Generate new entry
        result = self.generate(version=version, language=language)
        new_entry = result["changelog"]

        if not new_entry:
            return {"success": False, "error": "No new changes to add."}

        # Read existing changelog
        existing = ""
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                existing = f.read()

        # Insert new entry after header
        if existing:
            lines = existing.split("\n")
            # Find where to insert (after title and description)
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("## "):
                    insert_idx = i
                    break
            
            new_lines = lines[:insert_idx] + [new_entry, ""] + lines[insert_idx:]
            updated = "\n".join(new_lines)
        else:
            header = self._get_changelog_header(language)
            updated = header + "\n\n" + new_entry + "\n"

        # Write back
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(updated)
            return {
                "success": True,
                "path": output_path,
                "commits_count": result["commits_count"],
            }
        except IOError as e:
            return {"success": False, "error": str(e)}

    def _get_commits_since_tag(self, tag: str) -> List[GitCommit]:
        """Get commits since a specific tag."""
        result = self.git._run_git(["log", f"{tag}..HEAD", "--pretty=format:%H|%h|%s|%an|%ad|%d", "--date=short", "--numstat"])
        if result.returncode == 0:
            return self.git._parse_log(result.stdout)
        return []

    def _get_tags(self) -> List[str]:
        """Get list of git tags sorted by version."""
        result = self.git._run_git(["tag", "--sort=-v:refname"])
        if result.returncode == 0:
            return [t for t in result.stdout.strip().split("\n") if t]
        return []

    def _format_commits(self, commits: List[GitCommit]) -> str:
        """Format commits for prompt."""
        lines = []
        for commit in commits:
            lines.append(f"- [{commit.short_hash}] {commit.message} (by {commit.author})")
        return "\n".join(lines)

    def _get_changelog_header(self, language: str = "en") -> str:
        """Get changelog header in appropriate language."""
        headers = {
            "en": "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\nThe format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).",
            "zh": "# 更新日志\n\n此项目的所有重要变更都将记录在此文件中。\n\n格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。",
            "zh-tw": "# 更新日誌\n\n此專案的所有重要變更都將記錄在此文件中。\n\n格式基於 [Keep a Changelog](https://keepachangelog.com/)。",
        }
        return headers.get(language, headers["en"])
