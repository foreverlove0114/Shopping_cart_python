import sys
import os

# 确保能导入 main.py
sys.path.insert(0, os.path.abspath('.'))

def test_import_main():
    """验证能否成功导入 main.py"""
    try:
        from main import app, is_valid, allowed_file, parse, getLoginDetails
        assert app is not None
        assert callable(is_valid)
        assert callable(allowed_file)
        assert callable(parse)
        assert callable(getLoginDetails)
        print("✅ 所有导入成功！")
    except ImportError as e:
        assert False, f"导入失败: {e}"

def test_simple_math():
    """验证 pytest 基本功能"""
    assert 1 + 1 == 2

def test_hashlib_works():
    """验证 hashlib 是否正常工作"""
    import hashlib
    result = hashlib.md5('test'.encode()).hexdigest()
    assert result == '098f6bcd4621d373cade4e832627b4f6'
    print("✅ Hashlib 工作正常！")