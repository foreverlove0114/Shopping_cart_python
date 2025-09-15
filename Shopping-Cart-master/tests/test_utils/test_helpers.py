import pytest
import hashlib
import sqlite3
from unittest.mock import patch, MagicMock
from flask import session
from flask import Flask
import unittest

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

class TestHelperFunctions:
    """测试辅助函数"""

    def test_parse_function_with_empty_data(self):
        """测试 parse() 函数处理空数据"""
        # 行动
        result = parse([])
        # 断言
        assert result == []

    def test_parse_function_with_single_row(self):
        """测试 parse() 函数处理单行数据"""
        # 安排
        test_data = [1, 2, 3]
        # 行动
        result = parse(test_data)
        # 断言
        assert result == [[1, 2, 3]]

    def test_parse_function_with_multiple_rows(self):
        """测试 parse() 函数处理多行数据"""
        # 安排
        test_data = list(range(1, 15))  # 1-14
        # 行动
        result = parse(test_data)
        # 断言
        expected = [
            [1, 2, 3, 4, 5, 6, 7],
            [8, 9, 10, 11, 12, 13, 14]
        ]
        assert result == expected

    # @patch('main.session')  # 直接 mock session 对象
    # @patch('main.sqlite3.connect')
    # def test_get_login_details_logged_out(self, mock_connect, mock_session):
    #     """测试未登录时 getLoginDetails() 的返回"""
    #     # 安排：模拟空的 session
    #     mock_session.__contains__.return_value = False  # 模拟 'email' not in session
    #     mock_session.get.return_value = None
    #
    #     # 行动
    #     result = getLoginDetails()
    #
    #     # 断言
    #     assert result == (False, '', 0)
    #     mock_connect.assert_not_called()
    #
    # @patch('main.session')
    # @patch('main.sqlite3.connect')
    # def test_get_login_details_logged_in(self, mock_connect, mock_session):
    #     """测试登录时 getLoginDetails() 的返回"""
    #     # 安排 Mock
    #     mock_conn = MagicMock()
    #     mock_cur = MagicMock()
    #     mock_connect.return_value = mock_conn
    #     mock_conn.cursor.return_value = mock_cur
    #
    #     mock_cur.fetchone.side_effect = [
    #         (1, 'TestUser'),  # 用户信息
    #         (3,)  # 购物车数量
    #     ]
    #
    #     # 安排 Session Mock
    #     mock_session.__contains__.return_value = True  # 模拟 'email' in session
    #     mock_session.get.return_value = 'test@example.com'  # 模拟 session['email']
    #
    #     # 行动
    #     result = getLoginDetails()
    #
    #     # 断言
    #     assert result == (True, 'TestUser', 3)
    #     mock_connect.assert_called_once()
    #     assert mock_cur.execute.call_count == 2