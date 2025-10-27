#!/usr/bin/env python3
"""Unit tests for AI Learning Assistant."""

import os
import unittest
from unittest.mock import MagicMock, patch

import app as app_module
from app import DeepSeekClient, app


class TestAppEndpoints(unittest.TestCase):
    """Tests for Flask routes using a mocked DeepSeek client."""

    def setUp(self) -> None:
        os.environ["DEEPSEEK_API_KEY"] = "test_key"
        self.client = app.test_client()
        self.client.testing = True
        app_module.deepseek_client = MagicMock()

    def test_index_route_returns_html(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI", response.data)

    def test_health_endpoint_with_mocked_client(self) -> None:
        response = self.client.get("/api/health")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["deepseek_configured"])

    def test_chat_success(self) -> None:
        app_module.deepseek_client.chat_completion.return_value = {
            "choices": [{"message": {"content": "测试回复"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 40, "total_tokens": 50},
        }
        response = self.client.post("/api/chat", json={"message": "你好"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["reply"], "测试回复")
        self.assertIn("usage", payload)

    def test_chat_missing_message(self) -> None:
        response = self.client.post("/api/chat", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_chat_handles_exception(self) -> None:
        app_module.deepseek_client.chat_completion.side_effect = Exception("API错误")
        response = self.client.post("/api/chat", json={"message": "测试消息"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())

    def test_not_found_handler(self) -> None:
        response = self.client.get("/not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())


class TestDeepSeekClient(unittest.TestCase):
    """Tests for DeepSeekClient logic with OpenAI SDK mocked."""

    def setUp(self) -> None:
        os.environ["DEEPSEEK_API_KEY"] = "test_key"

    def test_init_without_api_key_raises(self) -> None:
        original_key = os.environ.pop("DEEPSEEK_API_KEY", None)
        try:
            with self.assertRaises(ValueError):
                DeepSeekClient()
        finally:
            if original_key:
                os.environ["DEEPSEEK_API_KEY"] = original_key

    @patch("app.OpenAI")
    def test_chat_completion_success(self, mock_openai: MagicMock) -> None:
        mock_choice = MagicMock()
        mock_choice.message.role = "assistant"
        mock_choice.message.content = "测试回复"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.prompt_tokens = 12
        mock_response.usage.completion_tokens = 18
        mock_response.usage.total_tokens = 30
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = DeepSeekClient()
        result = client.chat_completion("测试消息", max_tokens=128, temperature=0.7)

        self.assertEqual(result["choices"][0]["message"]["content"], "测试回复")
        self.assertEqual(result["usage"]["total_tokens"], 30)
        mock_openai.assert_called_once()

    @patch("app.OpenAI")
    def test_chat_completion_propagates_error(self, mock_openai: MagicMock) -> None:
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "timeout"
        )
        client = DeepSeekClient()
        with self.assertRaises(Exception):
            client.chat_completion("测试消息")
        mock_openai.return_value.chat.completions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
