"""
GitForge-CLI - Lightweight Terminal Git Workflow Intelligent Enhancement Engine
🔨 轻量级终端Git工作流智能增强引擎

AI-powered Git commit message generation, changelog creation, and workflow automation.
Zero-dependency core with GLM-5.1 integration.

Version: 1.0.0
Author: gitstq
License: MIT
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .core.git_analyzer import GitAnalyzer
from .core.commit_generator import CommitGenerator
from .core.changelog_generator import ChangelogGenerator
from .core.llm_client import GLMClient

__all__ = [
    "GitAnalyzer",
    "CommitGenerator",
    "ChangelogGenerator",
    "GLMClient",
]
