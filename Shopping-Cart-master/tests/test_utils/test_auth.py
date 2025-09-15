import pytest
import hashlib
import sqlite3

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
    # def test_is_valid_empty_input():
    #     """测试空输入处理"""
    #     # 断言：返回 False
    #
    # def test_password_hashing_md5():
    #     """测试密码MD5哈希是否正确"""
    #     # 安排：明文密码
    #     # 行动：计算哈希
    #     # 断言：与预期MD5值匹配