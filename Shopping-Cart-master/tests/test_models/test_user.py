import pytest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import hashlib
from io import BytesIO
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入应用
# 导入你的Flask应用
try:
    from ...main import app, is_valid, allowed_file, parse, getLoginDetails
except ImportError:
    # 如果相对导入失败，回退到绝对导入
    import os
    import sys

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    from main import app, is_valid, allowed_file, parse, getLoginDetails


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF用于测试
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_db():
    with patch('app.sqlite3.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor


def test_user_creation(client, mock_db):
    """测试用户创建成功"""
    mock_conn, mock_cursor = mock_db

    # 安排：用户数据
    user_data = {
        'email': 'test@example.com',
        'password': 'password123',
        'firstName': 'John',
        'lastName': 'Doe',
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'zipcode': '12345',
        'city': 'New York',
        'state': 'NY',
        'country': 'USA',
        'phone': '555-1234'
    }

    # 行动：注册用户
    response = client.post('/register', data=user_data)

    # 断言：验证数据库操作
    expected_password_hash = hashlib.md5(user_data['password'].encode()).hexdigest()
    mock_cursor.execute.assert_called_with(
        'INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (expected_password_hash, user_data['email'], user_data['firstName'],
         user_data['lastName'], user_data['address1'], user_data['address2'],
         user_data['zipcode'], user_data['city'], user_data['state'],
         user_data['country'], user_data['phone'])
    )
    mock_conn.commit.assert_called_once()

    # 断言：重定向到登录页面
    assert response.status_code == 200
    assert b'login' in response.data.lower()


def test_user_duplicate_email_rejection(client, mock_db):
    """测试重复邮箱注册被拒绝"""
    mock_conn, mock_cursor = mock_db

    # 安排：模拟数据库抛出完整性错误（重复邮箱）
    mock_conn.commit.side_effect = sqlite3.IntegrityError('UNIQUE constraint failed: users.email')

    # 行动：尝试注册重复邮箱用户
    user_data = {
        'email': 'duplicate@example.com',
        'password': 'password123',
        'firstName': 'Jane',
        'lastName': 'Smith',
        'address1': '456 Oak St',
        'address2': '',
        'zipcode': '67890',
        'city': 'Los Angeles',
        'state': 'CA',
        'country': 'USA',
        'phone': '555-5678'
    }

    response = client.post('/register', data=user_data)

    # 断言：验证回滚操作
    mock_conn.rollback.assert_called_once()

    # 断言：返回错误消息
    assert response.status_code == 200
    assert b'error occured' in response.data.lower() or b'error' in response.data.lower()


def test_user_password_stored_hashed(client, mock_db):
    """测试密码以哈希形式存储"""
    mock_conn, mock_cursor = mock_db

    # 安排：用户数据
    plain_password = 'mySecurePassword123'
    user_data = {
        'email': 'hash_test@example.com',
        'password': plain_password,
        'firstName': 'Test',
        'lastName': 'User',
        'address1': '789 Pine St',
        'address2': '',
        'zipcode': '11111',
        'city': 'Chicago',
        'state': 'IL',
        'country': 'USA',
        'phone': '555-9999'
    }

    # 行动：注册用户
    response = client.post('/register', data=user_data)

    # 断言：验证密码是哈希形式而不是明文
    call_args = mock_cursor.execute.call_args
    executed_sql = call_args[0][0]
    executed_params = call_args[0][1]

    # 检查SQL语句包含密码参数
    assert 'password' in executed_sql.lower()

    # 检查密码参数是哈希值而不是明文
    stored_password = executed_params[0]  # 第一个参数是密码
    assert stored_password != plain_password  # 不是明文
    assert len(stored_password) == 32  # MD5哈希长度
    assert stored_password == hashlib.md5(plain_password.encode()).hexdigest()  # 正确哈希


def test_user_required_fields_validation(client, mock_db):
    """测试必填字段验证"""
    mock_conn, mock_cursor = mock_db

    # 测试用例：缺少邮箱
    response = client.post('/register', data={
        'password': 'password123',
        'firstName': 'John',
        # 缺少 email
    })
    assert response.status_code == 200
    # 由于你的代码中没有前端验证，这里主要测试服务器不崩溃

    # 测试用例：缺少密码
    response = client.post('/register', data={
        'email': 'test@example.com',
        # 缺少 password
        'firstName': 'John',
    })
    assert response.status_code == 200

    # 测试用例：缺少firstName
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        # 缺少 firstName
    })
    assert response.status_code == 200


def test_user_login_success(client, mock_db):
    """测试用户登录成功"""
    mock_conn, mock_cursor = mock_db

    # 安排：模拟数据库返回用户数据
    test_email = 'test@example.com'
    test_password = 'password123'
    hashed_password = hashlib.md5(test_password.encode()).hexdigest()

    mock_cursor.fetchall.return_value = [
        (test_email, hashed_password)
    ]

    # 行动：登录
    with client:
        response = client.post('/login', data={
            'email': test_email,
            'password': test_password
        })

    # 断言：重定向到首页
    assert response.status_code == 302
    assert response.location == '/'

    # 断言：session中设置了email
    with client.session_transaction() as session:
        assert 'email' in session
        assert session['email'] == test_email


def test_user_login_failure(client, mock_db):
    """测试用户登录失败"""
    mock_conn, mock_cursor = mock_db

    # 安排：模拟数据库返回空结果（用户不存在）
    mock_cursor.fetchall.return_value = []

    # 行动：尝试登录
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })

    # 断言：返回登录页面并显示错误消息
    assert response.status_code == 200
    assert b'invalid' in response.data.lower() or b'error' in response.data.lower()

    # 断言：session中没有设置email
    with client.session_transaction() as session:
        assert 'email' not in session


def test_user_logout(client):
    """测试用户登出"""
    # 安排：先登录用户
    with client.session_transaction() as session:
        session['email'] = 'test@example.com'

    # 行动：登出
    response = client.get('/logout')

    # 断言：重定向到首页
    assert response.status_code == 302
    assert response.location == '/'

    # 断言：session中的email被清除
    with client.session_transaction() as session:
        assert 'email' not in session


def test_user_profile_access(client):
    """测试用户资料访问权限"""
    # 测试未登录用户访问资料页
    response = client.get('/account/profile')
    assert response.status_code == 302  # 重定向到首页

    # 测试已登录用户访问资料页
    with client.session_transaction() as session:
        session['email'] = 'test@example.com'

    response = client.get('/account/profile')
    assert response.status_code == 200  # 成功访问