"""
Commit Generator - AI-powered commit message generation following Conventional Commits.
AI驱动的提交信息生成器 - 遵循Conventional Commits规范。
"""

import re
from typing import List, Dict, Optional, Any
from .git_analyzer import GitAnalyzer, GitDiff
from .llm_client import GLMClient


class CommitGenerator:
    """
    Generate professional commit messages from git diffs using AI.
    Supports Conventional Commits specification.
    """

    COMMIT_TYPES = [
        "feat",      # New feature
        "fix",       # Bug fix
        "docs",      # Documentation
        "style",     # Code style (formatting)
        "refactor",  # Code refactoring
        "perf",      # Performance improvement
        "test",      # Tests
        "chore",     # Build/tooling changes
        "ci",        # CI/CD changes
        "build",     # Build system
        "revert",    # Revert changes
    ]

    SYSTEM_PROMPT = """You are GitForge, an expert Git commit message generator.
Analyze the provided git diff and generate a commit message following the Conventional Commits specification.

Rules:
1. Format: <type>(<scope>): <subject>
   - type: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert
   - scope: optional, the module/component affected (e.g., auth, api, ui, docs)
   - subject: concise description in imperative mood, max 50 chars

2. Body (optional): Detailed description if needed, wrapped at 72 chars
3. Footer (optional): Breaking changes, issue references

4. Language: Match the user's preferred language (detect from context)
5. Be specific and descriptive, avoid vague terms like "update" or "fix bug"

Output ONLY the commit message, no explanations or markdown formatting."""

    def __init__(self, llm_client: Optional[GLMClient] = None):
        self.llm_client = llm_client or GLMClient()
        self.git = GitAnalyzer()

    def generate(
        self,
        diff_content: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Generate commit message from diff.
        
        Returns dict with:
        - message: Full commit message
        - type: Commit type
        - scope: Commit scope
        - subject: Subject line
        - body: Message body
        - suggestions: Alternative messages
        """
        if not diff_content:
            diffs = self.git.get_staged_diff()
            if not diffs:
                return {
                    "message": "",
                    "type": "",
                    "scope": "",
                    "subject": "",
                    "body": "",
                    "suggestions": [],
                    "error": "No staged changes found. Stage files with 'git add' first.",
                }
            diff_content = self._format_diffs(diffs)

        # Build prompt
        prompt = self._build_prompt(diff_content, language, custom_prompt)

        # Generate with LLM
        response = self.llm_client.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3,
        )

        # Parse the generated message
        return self._parse_commit_message(response)

    def generate_batch(
        self,
        count: int = 3,
        diff_content: Optional[str] = None,
        language: str = "en",
    ) -> List[Dict[str, Any]]:
        """Generate multiple commit message options."""
        suggestions = []
        
        for i in range(count):
            temp = 0.3 + (i * 0.2)  # Increase temperature for variety
            if not diff_content:
                diffs = self.git.get_staged_diff()
                if not diffs:
                    break
                diff_content = self._format_diffs(diffs)
            
            prompt = self._build_prompt(diff_content, language)
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=temp,
            )
            parsed = self._parse_commit_message(response)
            if parsed["message"]:
                suggestions.append(parsed)
        
        return suggestions

    def _build_prompt(
        self,
        diff_content: str,
        language: str = "en",
        custom_prompt: Optional[str] = None,
    ) -> str:
        """Build the prompt for commit message generation."""
        lang_instruction = ""
        if language == "zh":
            lang_instruction = "\nPlease generate the commit message in Chinese (中文)."
        elif language == "zh-tw":
            lang_instruction = "\nPlease generate the commit message in Traditional Chinese (繁體中文)."

        base_prompt = f"""Analyze the following git diff and generate a professional commit message:

```diff
{diff_content[:4000]}
```

{lang_instruction}
"""
        if custom_prompt:
            base_prompt += f"\nAdditional context: {custom_prompt}"

        return base_prompt

    def _format_diffs(self, diffs: List[GitDiff]) -> str:
        """Format GitDiff objects into a string."""
        lines = []
        for diff in diffs:
            lines.append(f"File: {diff.file_path} ({diff.change_type})")
            lines.append(f"+{diff.additions}/-{diff.deletions}")
            if not diff.is_binary:
                lines.append(diff.diff_content[:2000])
            lines.append("---")
        return "\n".join(lines)

    def _parse_commit_message(self, message: str) -> Dict[str, Any]:
        """Parse generated commit message into components."""
        lines = message.strip().split("\n")
        if not lines:
            return {"message": "", "type": "", "scope": "", "subject": "", "body": "", "suggestions": []}

        # Parse subject line
        subject_line = lines[0].strip()
        
        # Remove markdown code blocks if present
        subject_line = re.sub(r'^```\w*\s*', '', subject_line)
        subject_line = re.sub(r'\s*```$', '', subject_line)

        # Parse conventional commit format
        pattern = r'^(\w+)(?:\(([^)]+)\))?!?:\s*(.+)$'
        match = re.match(pattern, subject_line)

        commit_type = ""
        scope = ""
        subject = subject_line

        if match:
            commit_type = match.group(1)
            scope = match.group(2) or ""
            subject = match.group(3)

        # Body is everything after subject line
        body = "\n".join(lines[1:]).strip()
        body = re.sub(r'^```\w*\s*', '', body)
        body = re.sub(r'\s*```$', '', body)

        return {
            "message": f"{subject_line}\n\n{body}".strip() if body else subject_line,
            "type": commit_type,
            "scope": scope,
            "subject": subject,
            "body": body,
            "suggestions": [],
        }

    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate a commit message against Conventional Commits spec."""
        issues = []
        warnings = []

        lines = message.strip().split("\n")
        if not lines or not lines[0]:
            issues.append("Commit message is empty")
            return {"valid": False, "issues": issues, "warnings": warnings}

        subject = lines[0]

        # Check format
        pattern = r'^(\w+)(?:\(([^)]+)\))?!?:\s*(.+)$'
        if not re.match(pattern, subject):
            issues.append("Subject doesn't follow Conventional Commits format: type(scope): subject")
        else:
            match = re.match(pattern, subject)
            commit_type = match.group(1)
            if commit_type not in self.COMMIT_TYPES:
                warnings.append(f"Type '{commit_type}' is not a standard type")

        # Check subject length
        if len(subject) > 72:
            warnings.append(f"Subject is {len(subject)} chars, consider keeping under 72")
        elif len(subject) > 50:
            warnings.append(f"Subject is {len(subject)} chars, ideal is under 50")

        # Check imperative mood
        non_imperative = ["added", "updated", "fixed", "changed", "removed", "deleted"]
        first_word = subject.split(":")[-1].strip().split()[0].lower()
        if first_word in non_imperative:
            warnings.append(f"Subject uses '{first_word}' - prefer imperative mood (add, update, fix)")

        # Check body line length
        for i, line in enumerate(lines[1:], 2):
            if len(line) > 100:
                warnings.append(f"Line {i} is {len(line)} chars, consider wrapping at 72")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }
