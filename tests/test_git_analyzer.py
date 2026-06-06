"""Tests for GitAnalyzer."""

import os
import subprocess
import tempfile
import shutil
import unittest

from gitforge.core.git_analyzer import GitAnalyzer


class TestGitAnalyzer(unittest.TestCase):
    """Test cases for GitAnalyzer."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
        
        self.git = GitAnalyzer()

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_is_git_repo(self):
        """Test git repo detection."""
        self.assertTrue(self.git.is_git_repo())

    def test_has_staged_changes(self):
        """Test staged changes detection."""
        self.assertFalse(self.git.has_staged_changes())
        
        # Create and stage a file
        with open("test.txt", "w") as f:
            f.write("hello")
        subprocess.run(["git", "add", "test.txt"], capture_output=True)
        
        self.assertTrue(self.git.has_staged_changes())

    def test_get_changed_files(self):
        """Test getting changed files."""
        with open("test.txt", "w") as f:
            f.write("hello")
        subprocess.run(["git", "add", "test.txt"], capture_output=True)
        
        files = self.git.get_changed_files(staged=True)
        self.assertIn("test.txt", files)

    def test_commit(self):
        """Test creating a commit."""
        with open("test.txt", "w") as f:
            f.write("hello")
        subprocess.run(["git", "add", "test.txt"], capture_output=True)
        
        self.assertTrue(self.git.commit("feat: add test file"))
        
        # Check commit exists
        result = subprocess.run(["git", "log", "-1", "--pretty=%s"], capture_output=True, text=True)
        self.assertIn("feat: add test file", result.stdout)

    def test_get_repo_info(self):
        """Test getting repo info."""
        info = self.git.get_repo_info()
        self.assertTrue(info["is_git_repo"])


if __name__ == "__main__":
    unittest.main()
