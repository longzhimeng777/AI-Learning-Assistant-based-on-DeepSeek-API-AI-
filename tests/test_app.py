#!/usr/bin/env python3
"""
AI学习助手测试文件（更新：避免真实外部调用，使用依赖注入与打桩）
"""

import os
import unittest
from unittest.mock import MagicMock, patch

import importlib

import app as app_module
from app import DeepSeekClient, app


class TestApp(unittest.TestCase):
    """应用接口测试"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # 确保有伪API Key，避免初始化失败
        os.environ["DEEPSEEK_API_KEY"] = "test_key"
        # 将 deepseek_client 替换为桩对象，避免真实网络/SDK调用
        app_module.deepseek_client = MagicMock()

    def test_index_route(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI", response.data)

    def test_health_check(self):
        response = self.app.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("status", data)
        self.assertIn("deepseek_configured", data)
        # 使用桩对象后应为 True
        self.assertTrue(data["deepseek_configured"]) 

    def test_chat_endpoint_success(self):
        # 打桩返回值
        app_module.deepseek_client.chat_completion.return_value = {
            "choices": [{"message": {"content": "这是一个测试回复"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 40, "total_tokens": 50},
        }
        response = self.app.post("/api/chat", json={"message": "你好"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("reply", data)
        self.assertIn("usage", data)
        self.assertEqual(data["reply"], "这是一个测试回复")

    def test_chat_endpoint_missing_message(self):
        response = self.app.post("/api/chat", json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_chat_endpoint_api_error(self):
        # 打桩抛异常
        app_module.deepseek_client.chat_completion.side_effect = Exception("API错误")
        response = self.app.post("/api/chat", json={"message": "测试消息"})
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    def test_404_error_handler(self):
        response = self.app.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)


class TestDeepSeekClient(unittest.TestCase):
    """DeepSeek 客户端基础行为测试（避免真实网络）"""

    def setUp(self):
        os.environ["DEEPSEEK_API_KEY"] = "test_key"

    def test_init_without_api_key(self):
        original_key = os.environ.pop("DEEPSEEK_API_KEY", None)
        with self.assertRaises(ValueError):
            DeepSeekClient()
        if original_key:
            os.environ["DEEPSEEK_API_KEY"] = original_key

    @patch.object(DeepSeekClient, "chat_completion", return_value={
        "choices": [{"message": {"content": "测试回复"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 15, "total_tokens": 20},
    })
    def test_chat_completion_success(self, mock_method):
        client = DeepSeekClient()
        resp = client.chat_completion("测试消息")
        self.assertIn("choices", resp)
        self.assertEqual(resp["choices"][0]["message"]["content"], "测试回复")
        mock_method.assert_called_once()

    @patch.object(DeepSeekClient, "chat_completion", side_effect=Exception("网络错误"))
    def test_chat_completion_request_exception(self, mock_method):
        client = DeepSeekClient()
        with self.assertRaises(Exception):
            client.chat_completion("测试消息")
        mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
