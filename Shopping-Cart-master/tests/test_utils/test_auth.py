import pytest
import hashlib

# 使用相对导入（需要先确保有 __init__.py 文件）
try:
    from ...main import is_valid, allowed_file, parse, getLoginDetails
except ImportError:
    # 如果相对导入失败，回退到绝对导入
    import os
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    from main import is_valid, allowed_file, parse, getLoginDetails

class TestAuthFunctions:

    def test_is_valid_with_correct_credentials(self,client):
        """测试正确用户名密码验证"""
        # 安排：创建测试用户
        # 行动：调用 is_valid('test@example.com', 'password')
        # 断言：返回 True
        test_email = "test@example.com"
        test_password = "password"

        result = is_valid(test_email,test_password)

        assert result is True



    def test_is_valid_with_incorrect_password():
        """测试错误密码验证"""
        # 断言：返回 False

    def test_is_valid_with_nonexistent_email():
        """测试不存在的邮箱验证"""
        # 断言：返回 False

    def test_is_valid_empty_input():
        """测试空输入处理"""
        # 断言：返回 False

    def test_password_hashing_md5():
        """测试密码MD5哈希是否正确"""
        # 安排：明文密码
        # 行动：计算哈希
        # 断言：与预期MD5值匹配