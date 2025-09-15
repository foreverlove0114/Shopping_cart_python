import pytest
import hashlib
import sqlite3
from unittest.mock import patch, MagicMock

# 使用相对导入（需要先确保有 __init__.py 文件）
try:
    from ...main import is_valid, allowed_file, parse, getLoginDetails
except ImportError:
    # 如果相对导入失败，回退到绝对导入
    import os
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    from main import app,is_valid, allowed_file, parse, getLoginDetails

##########################################################################################
class TestAuthFunctions:
    """测试认证工具函数"""

    @patch('main.sqlite3.connect')
    def test_is_valid_with_correct_credentials(self, mock_connect):
        """测试正确用户名密码验证"""
        # 安排 Mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        mock_data = [('test@example.com', '5f4dcc3b5aa765d61d8327deb882cf99')]
        mock_cur.fetchall.return_value = mock_data

        # 行动
        result = is_valid('test@example.com', 'password')

        # 断言
        assert result is True
        mock_connect.assert_called_once()
        mock_cur.execute.assert_called_once_with('SELECT email, password FROM users')

    @patch('main.sqlite3.connect')
    def test_is_valid_with_incorrect_password(self, mock_connect):
        """测试错误密码验证"""
        # 安排 Mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        mock_data = [('test@example.com', '5f4dcc3b5aa765d61d8327deb882cf99')]
        mock_cur.fetchall.return_value = mock_data

        # 行动
        result = is_valid('test@example.com', 'wrongpassword')

        # 断言
        assert result is False

    @patch('main.sqlite3.connect')
    def test_is_valid_with_nonexistent_email(self, mock_connect):
        """测试不存在的邮箱验证"""
        # 安排 Mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        mock_data = [('other@example.com', 'somehash')]
        mock_cur.fetchall.return_value = mock_data

        # 行动
        result = is_valid('nonexistent@example.com', 'password')

        # 断言
        assert result is False

    @patch('main.sqlite3.connect')
    def test_is_valid_empty_input(self, mock_connect):
        """测试空输入处理"""
        # 安排 Mock（但空输入应该不访问数据库）
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # 行动：测试各种空输入组合
        result1 = is_valid('', 'password')
        result2 = is_valid('test@example.com', '')
        result3 = is_valid('', '')

        # 断言：都应该返回 False，且不访问数据库
        assert result1 is False
        assert result2 is False
        assert result3 is False
        mock_connect.assert_not_called()

    def test_password_hashing_md5(self):
        """测试密码MD5哈希是否正确"""
        # 安排
        plain_password = "password"
        expected_hash = "5f4dcc3b5aa765d61d8327deb882cf99"

        # 行动
        actual_hash = hashlib.md5(plain_password.encode()).hexdigest()

        # 断言
        assert actual_hash == expected_hash