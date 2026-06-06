"""Tests for ChangelogGenerator."""

import unittest

from gitforge.core.changelog_generator import ChangelogGenerator


class TestChangelogGenerator(unittest.TestCase):
    """Test cases for ChangelogGenerator."""

    def setUp(self):
        self.gen = ChangelogGenerator()

    def test_get_changelog_header(self):
        """Test changelog header generation."""
        header_en = self.gen._get_changelog_header("en")
        self.assertIn("Changelog", header_en)
        
        header_zh = self.gen._get_changelog_header("zh")
        self.assertIn("更新日志", header_zh)

    def test_format_commits(self):
        """Test commit formatting."""
        from gitforge.core.git_analyzer import GitCommit
        commits = [
            GitCommit("abc123", "abc", "feat: add feature", "Test", "2026-01-01"),
        ]
        text = self.gen._format_commits(commits)
        self.assertIn("feat: add feature", text)
        self.assertIn("Test", text)

    def test_mock_generation(self):
        """Test mock mode generation."""
        result = self.gen.generate(version="1.0.0")
        self.assertIn("Mock Mode", result["changelog"])


if __name__ == "__main__":
    unittest.main()
