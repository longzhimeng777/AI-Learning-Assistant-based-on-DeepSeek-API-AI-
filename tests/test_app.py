
#!/usr/bin/env python3
"""
AI学习助手测试文件
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from app import DeepSeekClient, app


class TestApp(unittest.TestCase):
    """应用测试类"""

    def setUp(self):
        """测试前设置"""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        """测试主页路由"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI", response.data)

    def test_health_check(self):
        """测试健康检查接口"""
        response = self.app.get("/api/health")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("status", data)
        self.assertIn("deepseek_configured", data)
        self.assertEqual(data["status"], "healthy")

    @patch("app.requests.post")
    def test_chat_endpoint_success(self, mock_post):
        """测试聊天接口成功情况"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "这是一个测试回复"}}],
            "usage": {"total_tokens": 50},
        }
        mock_post.return_value = mock_response

        # 发送请求
        response = self.app.post("/api/chat", json={"message": "你好"})

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("reply", data)
        self.assertIn("usage", data)
        self.assertEqual(data["reply"], "这是一个测试回复")

    def test_chat_endpoint_missing_message(self):
        """测试聊天接口缺少message参数"""
        response = self.app.post("/api/chat", json={})

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("app.requests.post")
    def test_chat_endpoint_api_error(self, mock_post):
        """测试聊天接口API错误"""
        # 模拟API错误
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API错误")
        mock_post.return_value = mock_response

        response = self.app.post("/api/chat", json={"message": "测试消息"})

        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    def test_404_error_handler(self):
        """测试404错误处理"""
        response = self.app.get("/nonexistent")

        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)


class TestDeepSeekClient(unittest.TestCase):
    """DeepSeek客户端测试类"""

    def setUp(self):
        """测试前设置"""
        # 设置环境变量
        os.environ["DEEPSEEK_API_KEY"] = "test_key"
        self.client = DeepSeekClient()

    def test_init_without_api_key(self):
        """测试没有API密钥时的初始化"""
        # 临时移除API密钥
        original_key = os.environ.pop("DEEPSEEK_API_KEY", None)

        with self.assertRaises(ValueError):
            DeepSeekClient()

        # 恢复环境变量
        if original_key:
            os.environ["DEEPSEEK_API_KEY"] = original_key

    @patch("app.requests.post")
    def test_chat_completion_success(self, mock_post):
        """测试聊天补全成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "测试回复"}}]
        }
        mock_post.return_value = mock_response

        response = self.client.chat_completion("测试消息")

        self.assertIn("choices", response)
        self.assertEqual(response["choices"][0]["message"]["content"], "测试回复")

        # 验证请求参数
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn("headers", call_args.kwargs)
        self.assertIn("json", call_args.kwargs)

    @patch("app.requests.post")
    def test_chat_completion_with_parameters(self, mock_post):
        """测试带参数的聊天补全"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "回复"}}]}
        mock_post.return_value = mock_response

        # 验证参数传递
        call_args = mock_post.call_args
        request_data = call_args.kwargs["json"]

        self.assertEqual(request_data["max_tokens"], 100)
        self.assertEqual(request_data["temperature"], 0.8)

    @patch("app.requests.post")
    def test_chat_completion_request_exception(self, mock_post):
        """测试请求异常"""
        mock_post.side_effect = Exception("网络错误")

        with self.assertRaises(Exception):
            self.client.chat_completion("测试消息")


if __name__ == "__main__":
    unittest.main()
