"""Tests for GLMClient."""

import unittest

from gitforge.core.llm_client import GLMClient


class TestGLMClient(unittest.TestCase):
    """Test cases for GLMClient."""

    def test_mock_mode(self):
        """Test mock mode without API key."""
        client = GLMClient()
        self.assertTrue(client._mock_mode)
        self.assertFalse(client.is_configured())

    def test_with_api_key(self):
        """Test with API key."""
        client = GLMClient(api_key="test-key")
        self.assertFalse(client._mock_mode)
        self.assertTrue(client.is_configured())

    def test_mock_response(self):
        """Test mock response generation."""
        client = GLMClient()
        response = client.chat([{"role": "user", "content": "Hello"}])
        self.assertIn("choices", response)
        self.assertTrue(len(response["choices"]) > 0)
        content = response["choices"][0]["message"]["content"]
        self.assertIn("Mock Mode", content)

    def test_generate(self):
        """Test generate method."""
        client = GLMClient()
        result = client.generate("Test prompt")
        self.assertIn("Mock Mode", result)

    def test_model_info(self):
        """Test model info."""
        client = GLMClient(api_key="test", model="custom-model")
        info = client.get_model_info()
        self.assertEqual(info["model"], "custom-model")


if __name__ == "__main__":
    unittest.main()
