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
#连接测试数据库
    def test_is_valid_with_db(email, password, db_path):
        """测试专用的验证函数"""
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute('SELECT email, password FROM users')
        data = cur.fetchall()
        for row in data:
            if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
                con.close()
                return True
        con.close()
        return False


##########################################################################################
class TestAuthFunctions:

    def test_is_valid_with_correct_credentials(self, client):
        """测试正确用户名密码验证"""
        # 获取测试数据库路径（需要通过 app 配置获取）
        test_db_path = app.config['DATABASE']

        test_email = "test@example.com"
        test_password = "password"

        result = test_is_valid_with_db(test_email, test_password, test_db_path)
        expected_result = True
        assert result == expected_result


    def test_is_valid_with_incorrect_password(self,client):
        """测试错误密码验证"""
        # 断言：返回 False
        test_db_path = app.config['DATABASE']

        test_email = "test@example.com"
        test_password = "pass"

        result = test_is_valid_with_db(test_email,test_password,test_db_path)
        expected_result = False
        assert result == expected_result
    #
    def test_is_valid_with_nonexistent_email(self,client):
        """测试不存在的邮箱验证"""
        # 断言：返回 False
        test_db_path = app.config['DATABASE']

        test_email = "te@example.com"
        test_password = "pass"

        result = test_is_valid_with_db(test_email,test_password,test_db_path)
        expected_result = False
        assert result == expected_result
    #
    def test_is_valid_empty_input(self,client):
        """测试空输入处理"""
        # 断言：返回 False
        test_db_path = app.config['DATABASE']

        test_email = ""
        test_password = ""

        result = test_is_valid_with_db(test_email,test_password,test_db_path)
        expected_result = False
        assert result == expected_result

    #
    def test_password_hashing_md5(self):
        """测试密码MD5哈希是否正确"""
        # 安排：明文密码
        # 行动：计算哈希
        # 断言：与预期MD5值匹配
        input_password = "password"
        expected_hash = "5f4dcc3b5aa765d61d8327deb882cf99"

        actual_hash = hashlib.md5(input_password.encode()).hexdigest()
        # 打印信息（使用 -s 参数才能看到）
        # print(f"\n输入密码: {input_password}")
        # print(f"期望哈希: {expected_hash}")
        # print(f"实际哈希: {actual_hash}")
        assert actual_hash == expected_hash, f"期望: {expected_hash}, 实际: {actual_hash}"

    def test_allowed_file_extensions(self):
        """测试允许的文件扩展名"""
        assert allowed_file('image.jpg') is True
        """测试不允许的文件扩展名"""
        assert allowed_file('document.pdf') is False
        """测试没有扩展名的文件"""
        assert allowed_file('file') is False
        """测试边界情况"""
        assert allowed_file('.jpg') is False  # 只有扩展名

    def test_parse_data(self):
        data1 = [1,2,3,4,5,6]
        result1 = parse(data1)
        assert result1 == [data1]

        """测试正好多组7个元素的数据"""
        data = list(range(1, 15))  # 1-14
        result = parse(data)
        expected = [
            [1, 2, 3, 4, 5, 6, 7],
            [8, 9, 10, 11, 12, 13, 14]
        ]
        assert result == expected

##########################################################################################
##########################################################################################
##########################################################################################
#使用mock

    @patch('main.sqlite3.connect') #mock 数据库连接
    def test_is_valid_with_correct_credentials_mock(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        mock_data = [
            ('test@exmaple.com','5f4dcc3b5aa765d61d8327deb882cf99'),
            ('other@example.com','otherhash')
        ]

        mock_cur.fetchall.return_value = mock_data  # 模拟查询结果

        result = is_valid('test@exmaple.com','password')

        assert result is True  # 应该返回 True（验证成功）
        mock_connect.assert_called_once()  # 确保数据库连接只被调用一次
        mock_cur.execute.assert_called_once_with('SELECT email, password FROM users')
        # 确保执行了正确的 SQL 查询

    @patch('main.sqlite3.connect')
    def test_is_valid_with_incorrect_password_mock(self, mock_connect):
        # 设置 mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # 1. 配置 Mock 行为 ✅
        mock_data = [('test@example.com', '5f4dcc3b5aa765d61d8327deb882cf99')]
        mock_cur.fetchall.return_value = mock_data  # ⚠️ 这行绝对不能漏！

        # 执行测试
        result = is_valid('test@example.com', 'wrongpassword')

        # 2. 验证 Mock 调用 ✅
        mock_connect.assert_called_once()
        mock_cur.execute.assert_called_once_with('SELECT email, password FROM users')
        mock_cur.fetchall.assert_called_once()  # 现在这个验证才有意义

        # 3. 验证业务结果 ✅
        assert result is False

    @patch('main.sqlite3.connect')
    def test_is_valid_with_nonexistent_email_mock(self,mock_connect):
        """测试不存在的邮箱验证"""
        # 断言：返回 False
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        mock_data = [('test@example.com', '5f4dcc3b5aa765d61d8327deb882cf99')]
        mock_cur.fetchall.return_value = mock_data

        result = is_valid('te@example.com', 'password')

        assert result is False

    @patch('main.sqlite3.connect')
    def test_is_valid_empty_input_mock(self, mock_connect):
        """测试空输入处理 - 使用 mock"""
        # 即使数据库有数据，空输入也应该返回 False
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        mock_data = [('test@example.com', '5f4dcc3b5aa765d61d8327deb882cf99')]
        mock_cur.fetchall.return_value = mock_data

        result = is_valid('', 'password')
        assert result is False

        result = is_valid('test@example.com', '')
        assert result is False

        result = is_valid('', '')
        assert result is False
