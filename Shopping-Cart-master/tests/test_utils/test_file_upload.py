import pytest
import hashlib
import sqlite3
from unittest.mock import patch

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


class TestFileUpload:
    """测试文件上传功能"""

    def test_allowed_file_valid_extensions(self):
        """测试允许的文件扩展名"""
        # 对每个允许的扩展名进行测试
        valid_files = [
            'image.jpg',
            'photo.jpeg',
            'picture.png',
            'animation.gif',
            'document.JPG',  # 大写
            'photo.JPEG',
            'image.PNG',
            'anim.GIF'
        ]

        for filename in valid_files:
            assert allowed_file(filename) is True, f"{filename} 应该被允许"

    def test_allowed_file_invalid_extensions(self):
        """测试不允许的文件扩展名"""
        invalid_files = [
            'document.pdf',
            'script.js',
            'file.txt',
            'program.exe',
            'archive.zip',
            'video.mp4'
        ]

        for filename in invalid_files:
            assert allowed_file(filename) is False, f"{filename} 应该被拒绝"

    def test_allowed_file_no_extension(self):
        """测试无扩展名的文件"""
        no_extension_files = [
            'file',
            'image',
            'no_extension',
            'file.',
            '.'
        ]

        for filename in no_extension_files:
            assert allowed_file(filename) is False, f"{filename} 应该被拒绝"

    def test_allowed_file_only_extension(self):
        """测试只有扩展名的文件"""
        only_extension_files = [
            '.jpg',
            '.png',
            '.gif',
            '.jpeg'
        ]

        for filename in only_extension_files:
            assert allowed_file(filename) is False, f"{filename} 应该被拒绝"
