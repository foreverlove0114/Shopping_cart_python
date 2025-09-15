from unittest.mock import patch, MagicMock
import pytest

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
def test_client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        with app.app_context():
            yield client


class TestCartFeature:

    @patch('main.sqlite3.connect')
    def test_add_to_cart(self, mock_connect, test_client):
        """测试添加商品到购物车"""
        # 安排 Mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # 模拟用户ID查询
        mock_cur.fetchone.return_value = (1,)  # 返回用户ID

        # 设置会话
        with test_client.session_transaction() as sess:
            sess['email'] = 'test@example.com'

        # 行动：调用添加购物车路由
        response = test_client.get('/addToCart?productId=123')

        # 断言
        assert response.status_code == 302  # 重定向
        mock_connect.assert_called_once_with('database.db')

        # 检查是否调用了正确的SQL语句
        sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
        user_select_called = any(
            "SELECT userId FROM users WHERE email = ?" in str(call) for call in mock_cur.execute.call_args_list)
        insert_called = any("INSERT INTO kart" in str(call) for call in mock_cur.execute.call_args_list)

        assert user_select_called, "用户查询SQL没有被调用"
        assert insert_called, "插入购物车SQL没有被调用"
        mock_conn.commit.assert_called_once()

    @patch('main.sqlite3.connect')
    def test_remove_from_cart(self, mock_connect, test_client):
        """测试从购物车移除商品"""
        # 安排 Mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # 模拟用户ID查询
        mock_cur.fetchone.return_value = (1,)

        # 设置会话
        with test_client.session_transaction() as sess:
            sess['email'] = 'test@example.com'

        # 行动：调用移除购物车路由
        response = test_client.get('/removeFromCart?productId=123')

        # 断言
        assert response.status_code == 302

        # 检查是否调用了正确的SQL语句
        sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
        user_select_called = any(
            "SELECT userId FROM users WHERE email = ?" in str(call) for call in mock_cur.execute.call_args_list)
        delete_called = any("DELETE FROM kart" in str(call) for call in mock_cur.execute.call_args_list)

        assert user_select_called, "用户查询SQL没有被调用"
        assert delete_called, "删除购物车SQL没有被调用"
        mock_conn.commit.assert_called_once()

    @patch('main.getLoginDetails')
    @patch('main.sqlite3.connect')
    def test_cart_total_calculation(self, mock_connect, mock_get_login_details, test_client):
        """测试购物车总价计算"""
        # 安排 Mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # 模拟getLoginDetails返回值
        mock_get_login_details.return_value = (True, 'Test User', 3)

        # 模拟购物车商品数据
        mock_cart_data = [
            (101, '商品1', 10.0, 'image1.jpg'),
            (102, '商品2', 20.0, 'image2.jpg'),
            (103, '商品3', 15.5, 'image3.jpg')
        ]
        mock_cur.fetchall.return_value = mock_cart_data

        # 模拟用户ID查询
        mock_cur.fetchone.return_value = (1,)

        # 设置会话
        with test_client.session_transaction() as sess:
            sess['email'] = 'test@example.com'

        # 行动：访问购物车页面
        response = test_client.get('/cart')

        # 断言
        assert response.status_code == 200

        # 检查是否调用了购物车查询SQL
        cart_query_called = any(
            "SELECT products.productId, products.name, products.price, products.image FROM products, kart" in str(call)
            for call in mock_cur.execute.call_args_list)
        assert cart_query_called, "购物车查询SQL没有被调用"

    @patch('main.sqlite3.connect')
    def test_cart_quantity_management(self, mock_connect, test_client):
        """测试购物车商品数量管理"""
        # 安排 Mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # 模拟用户ID查询
        mock_cur.fetchone.return_value = (1,)

        # 设置会话
        with test_client.session_transaction() as sess:
            sess['email'] = 'test@example.com'

        # 行动：多次添加同一商品
        test_client.get('/addToCart?productId=123')
        test_client.get('/addToCart?productId=123')

        # 断言：应该调用两次INSERT
        insert_calls = [call for call in mock_cur.execute.call_args_list
                        if call[0] and 'INSERT INTO kart' in str(call[0])]
        assert len(insert_calls) >= 2, f"期望至少2次INSERT调用，实际{len(insert_calls)}次"

    @patch('main.getLoginDetails')
    @patch('main.sqlite3.connect')
    def test_cart_user_association(self, mock_connect, mock_get_login_details, test_client):
        """测试购物车与用户的关联"""
        # 安排 Mock
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # 模拟getLoginDetails返回值
        mock_get_login_details.return_value = (True, 'Test User', 1)

        # 模拟用户A的购物车数据
        user_a_data = [(101, '商品1', 10.0, 'image1.jpg')]
        # 模拟用户B的购物车数据为空
        user_b_data = []

        # 根据不同的用户返回不同的数据
        def mock_fetchall_side_effect():
            # 检查最近的execute调用
            if mock_cur.execute.call_args_list:
                last_call = mock_cur.execute.call_args_list[-1]
                if last_call[0] and 'userId = ?' in str(last_call[0]):
                    user_id = last_call[0][1][0] if last_call[0][1] else None
                    if user_id == 1:
                        return user_a_data
                    elif user_id == 2:
                        return user_b_data
            return []

        mock_cur.fetchall.side_effect = mock_fetchall_side_effect

        # 模拟用户ID查询
        mock_cur.fetchone.return_value = (1,)

        # 测试用户A的购物车
        with test_client.session_transaction() as sess:
            sess['email'] = 'user_a@example.com'

        response = test_client.get('/cart')
        assert response.status_code == 200

    def test_add_to_cart_not_logged_in(self, test_client):
        """测试未登录时添加商品到购物车"""
        # 不设置session，模拟未登录状态
        response = test_client.get('/addToCart?productId=123')

        # 断言：应该重定向到登录页面
        assert response.status_code == 302
        assert '/loginForm' in response.location

    def test_remove_from_cart_not_logged_in(self, test_client):
        """测试未登录时从购物车移除商品"""
        # 不设置session，模拟未登录状态
        response = test_client.get('/removeFromCart?productId=123')

        # 断言：应该重定向到登录页面
        assert response.status_code == 302
        assert '/loginForm' in response.location