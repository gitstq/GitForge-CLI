"""
LLM Client - GLM-5.1 API integration for commit and changelog generation.
GLM-5.1 API 集成客户端。
"""

import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Iterator, List


class GLMClient:
    """
    Client for GLM-5.1 API with support for streaming and non-streaming requests.
    Falls back to mock mode if no API key is provided.
    """

    DEFAULT_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
    DEFAULT_MODEL = "glm-5.1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ):
        self.api_key = api_key or os.environ.get("GLM_API_KEY", "")
        self.api_base = api_base or os.environ.get("GLM_API_BASE", self.DEFAULT_API_BASE)
        self.model = model or os.environ.get("GLM_MODEL", self.DEFAULT_MODEL)
        self.timeout = timeout
        self._mock_mode = not self.api_key

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        return headers

    def _make_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to GLM API."""
        url = f"{self.api_base}/chat/completions"
        headers = self._build_headers()

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_data = json.loads(error_body)
                raise GLMAPIError(
                    f"API Error: {error_data.get('error', {}).get('message', error_body)}"
                )
            except json.JSONDecodeError:
                raise GLMAPIError(f"HTTP Error {e.code}: {error_body}")
        except Exception as e:
            raise GLMAPIError(f"Request failed: {str(e)}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Send chat completion request."""
        if self._mock_mode:
            return self._mock_response(messages)

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        return self._make_request(data)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """Generate text from a prompt."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.chat(messages, temperature=temperature, max_tokens=max_tokens)

        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        return ""

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Iterator[str]:
        """Stream generate text from a prompt."""
        if self._mock_mode:
            yield self._mock_response([{"role": "user", "content": prompt}])
            return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }

        url = f"{self.api_base}/chat/completions"
        headers = self._build_headers()

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                for line in response:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate mock response for testing without API key."""
        last_message = messages[-1]["content"] if messages else ""

        mock_answer = (
            "🤖 [Mock Mode] This is a simulated response.\n\n"
            "To get real AI-generated commit messages, please set your GLM API key:\n"
            "  export GLM_API_KEY='your-api-key'\n\n"
            f"Your prompt was: {last_message[:100]}...\n\n"
            "In real mode, I would analyze your git diff and generate "
            "a professional Conventional Commit message."
        )

        return {
            "choices": [{
                "message": {"role": "assistant", "content": mock_answer},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    def is_configured(self) -> bool:
        """Check if API is properly configured."""
        return bool(self.api_key)

    def get_model_info(self) -> Dict[str, str]:
        """Get current model configuration."""
        return {
            "model": self.model,
            "api_base": self.api_base,
            "configured": str(self.is_configured()),
            "mock_mode": str(self._mock_mode),
        }


class GLMAPIError(Exception):
    """Exception for GLM API errors."""
    pass
