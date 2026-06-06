"""Tests for CommitGenerator."""

import unittest

from gitforge.core.commit_generator import CommitGenerator


class TestCommitGenerator(unittest.TestCase):
    """Test cases for CommitGenerator."""

    def setUp(self):
        self.gen = CommitGenerator()

    def test_parse_commit_message(self):
        """Test parsing commit message."""
        message = "feat(auth): add login functionality\n\nThis adds user login with JWT tokens."
        result = self.gen._parse_commit_message(message)
        
        self.assertEqual(result["type"], "feat")
        self.assertEqual(result["scope"], "auth")
        self.assertEqual(result["subject"], "add login functionality")
        self.assertIn("JWT tokens", result["body"])

    def test_parse_without_scope(self):
        """Test parsing message without scope."""
        message = "fix: resolve memory leak"
        result = self.gen._parse_commit_message(message)
        
        self.assertEqual(result["type"], "fix")
        self.assertEqual(result["scope"], "")
        self.assertEqual(result["subject"], "resolve memory leak")

    def test_validate_valid_message(self):
        """Test validating a valid message."""
        message = "feat: add new feature"
        result = self.gen.validate_message(message)
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["issues"]), 0)

    def test_validate_invalid_format(self):
        """Test validating invalid format."""
        message = "add new feature"
        result = self.gen.validate_message(message)
        
        self.assertFalse(result["valid"])
        self.assertTrue(len(result["issues"]) > 0)

    def test_validate_long_subject(self):
        """Test validating long subject."""
        message = "feat: " + "x" * 100
        result = self.gen.validate_message(message)
        
        self.assertTrue(result["valid"])
        self.assertTrue(len(result["warnings"]) > 0)

    def test_validate_non_imperative(self):
        """Test detecting non-imperative mood."""
        message = "feat: added new feature"
        result = self.gen.validate_message(message)
        
        self.assertTrue(result["valid"])
        self.assertTrue(any("added" in w for w in result["warnings"]))

    def test_mock_generation(self):
        """Test mock mode generation."""
        result = self.gen.generate(diff_content="some diff content")
        self.assertIn("Mock Mode", result["message"])


if __name__ == "__main__":
    unittest.main()
