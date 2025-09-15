import pytest
import os
import sys
import tempfile
import sqlite3
from typing import TYPE_CHECKING

# 为编辑器提供类型提示
if TYPE_CHECKING:
    from flask import Flask
    from typing import Callable, Any, Tuple

    app: Flask
    is_valid: Callable[[str, str], bool]
    allowed_file: Callable[[str], bool]
    parse: Callable[[list], list]
    getLoginDetails: Callable[[], Tuple[bool, str, int]]

# 使用绝对路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 实际导入
from main import app, is_valid, allowed_file, parse, getLoginDetails


@pytest.fixture
def client():
    """创建测试客户端"""
    # 创建临时数据库用于测试
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path

    # 初始化测试数据库
    with app.app_context():
        init_test_database(db_path)

    with app.test_client() as client:
        yield client

    # 测试结束后清理
    os.close(db_fd)
    os.unlink(db_path)


def init_test_database(db_path):
    """初始化测试数据库"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 创建测试表结构（从你的 main.py 中复制）
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userId INTEGER PRIMARY KEY AUTOINCREMENT,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            address1 TEXT NOT NULL,
            address2 TEXT NOT NULL,
            zipcode TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            country TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')

    # 插入测试数据
    cur.execute('''
        INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('5f4dcc3b5aa765d61d8327deb882cf99', 'test@example.com', 'Test', 'User', '123 Main St', '', '12345', 'City',
          'State', 'Country', '1234567890'))

    conn.commit()
    conn.close()


@pytest.fixture
def auth_functions():
    """提供认证相关函数"""
    return {
        'is_valid': is_valid,
        'hashlib': __import__('hashlib')
    }