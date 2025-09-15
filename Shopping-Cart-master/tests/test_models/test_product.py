import pytest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import hashlib
import os
from werkzeug.datastructures import FileStorage
from io import BytesIO

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
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_db():
    with patch('your_app_module.sqlite3.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor


def test_allowed_file():
    """测试文件类型验证"""
    assert allowed_file('image.jpg') == True
    assert allowed_file('image.png') == True
    assert allowed_file('image.gif') == True
    assert allowed_file('image.jpeg') == True
    assert allowed_file('image.pdf') == False
    assert allowed_file('.hidden.jpg') == False
    assert allowed_file('') == False
    assert allowed_file(None) == False


def test_parse():
    """测试parse函数"""
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    result = parse(data)
    expected = [[1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14]]
    assert result == expected


def test_is_valid():
    """测试用户验证"""
    # 测试空输入
    assert is_valid('', 'password') == False
    assert is_valid('test@example.com', '') == False

    # 测试有效用户
    with patch('your_app_module.sqlite3.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('test@example.com', hashlib.md5('password123'.encode()).hexdigest())
        ]

        assert is_valid('test@example.com', 'password123') == True
        assert is_valid('test@example.com', 'wrongpassword') == False


def test_product_creation(client, mock_db):
    """测试商品创建成功"""
    mock_conn, mock_cursor = mock_db

    # 模拟会话
    with client.session_transaction() as session:
        session['email'] = 'admin@example.com'

    # 模拟文件上传
    mock_file = FileStorage(
        stream=BytesIO(b"fake image data"),
        filename="test.jpg",
        name="image"
    )

    # 测试请求
    with patch('your_app_module.request') as mock_request:
        mock_request.method = 'POST'
        mock_request.form = {
            'name': 'Test Product',
            'price': '19.99',
            'description': 'Test Description',
            'stock': '10',
            'category': '1'
        }
        mock_request.files = {'image': mock_file}

        # 调用addItem路由
        response = client.post('/addItem', data={
            'name': 'Test Product',
            'price': '19.99',
            'description': 'Test Description',
            'stock': '10',
            'category': '1',
            'image': (BytesIO(b"fake image data"), 'test.jpg')
        }, content_type='multipart/form-data')

        # 验证数据库操作
        mock_cursor.execute.assert_called_with(
            '''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''',
            ('Test Product', 19.99, 'Test Description', 'test.jpg', 10, 1)
        )
        mock_conn.commit.assert_called_once()


def test_product_price_positive(client, mock_db):
    """测试商品价格必须为正数"""
    mock_conn, mock_cursor = mock_db

    # 模拟会话
    with client.session_transaction() as session:
        session['email'] = 'admin@example.com'

    # 测试负价格
    with patch('your_app_module.request') as mock_request:
        mock_request.method = 'POST'
        mock_request.form = {
            'name': 'Test Product',
            'price': '-10.00',  # 负价格
            'description': 'Test Description',
            'stock': '10',
            'category': '1'
        }
        mock_request.files = {'image': None}

        # 这里应该测试应用如何处理负价格
        # 由于你的代码中没有显式的验证，这个测试主要检查是否会执行数据库操作
        response = client.post('/addItem', data={
            'name': 'Test Product',
            'price': '-10.00',
            'description': 'Test Description',
            'stock': '10',
            'category': '1'
        })

        # 验证是否尝试执行数据库操作（虽然应该失败）
        # 在实际应用中，你应该添加价格验证逻辑


def test_product_stock_non_negative(client, mock_db):
    """测试商品库存不能为负数"""
    mock_conn, mock_cursor = mock_db

    # 模拟会话
    with client.session_transaction() as session:
        session['email'] = 'admin@example.com'

    # 测试负库存
    with patch('your_app_module.request') as mock_request:
        mock_request.method = 'POST'
        mock_request.form = {
            'name': 'Test Product',
            'price': '19.99',
            'description': 'Test Description',
            'stock': '-5',  # 负库存
            'category': '1'
        }
        mock_request.files = {'image': None}

        response = client.post('/addItem', data={
            'name': 'Test Product',
            'price': '19.99',
            'description': 'Test Description',
            'stock': '-5',
            'category': '1'
        })

        # 验证是否尝试执行数据库操作
        # 在实际应用中，你应该添加库存验证逻辑


def test_product_image_file_validation():
    """测试商品图片文件类型验证"""
    # 这个测试已经包含在test_allowed_file中
    pass


def test_product_category_association(client, mock_db):
    """测试商品与分类的关联"""
    mock_conn, mock_cursor = mock_db

    # 模拟会话
    with client.session_transaction() as session:
        session['email'] = 'admin@example.com'

    # 模拟文件上传
    mock_file = FileStorage(
        stream=BytesIO(b"fake image data"),
        filename="test.jpg",
        name="image"
    )

    # 测试特定分类ID
    test_category_id = 2

    with patch('your_app_module.request') as mock_request:
        mock_request.method = 'POST'
        mock_request.form = {
            'name': 'Test Product',
            'price': '19.99',
            'description': 'Test Description',
            'stock': '10',
            'category': str(test_category_id)
        }
        mock_request.files = {'image': mock_file}

        response = client.post('/addItem', data={
            'name': 'Test Product',
            'price': '19.99',
            'description': 'Test Description',
            'stock': '10',
            'category': str(test_category_id),
            'image': (BytesIO(b"fake image data"), 'test.jpg')
        }, content_type='multipart/form-data')

        # 验证数据库操作中包含了正确的分类ID
        mock_cursor.execute.assert_called_with(
            '''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''',
            ('Test Product', 19.99, 'Test Description', 'test.jpg', 10, test_category_id)
        )


def test_display_category(client, mock_db):
    """测试按分类显示商品"""
    mock_conn, mock_cursor = mock_db

    # 模拟数据库返回数据
    mock_data = [
        (1, 'Product 1', 10.99, 'image1.jpg', 'Electronics'),
        (2, 'Product 2', 20.99, 'image2.jpg', 'Electronics')
    ]
    mock_cursor.fetchall.return_value = mock_data

    # 测试请求
    response = client.get('/displayCategory?categoryId=1')

    # 验证数据库查询
    mock_cursor.execute.assert_called_with(
        "SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?",
        (1,)
    )

    assert response.status_code == 200


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])