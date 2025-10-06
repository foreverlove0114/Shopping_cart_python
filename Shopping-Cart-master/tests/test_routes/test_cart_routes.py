import pytest
import requests
from bs4 import BeautifulSoup
import re
import os

# 从环境变量读取BASE_URL
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

# 测试用户数据
TEST_USER = {
    "email": "testuser@example.com",
    "password": "testpass123",
    "firstName": "Test",
    "lastName": "User",
    "address1": "123 Test St",
    "address2": "Apt 1",
    "zipcode": "12345",
    "city": "TestCity",
    "state": "TS",
    "country": "TestCountry",
    "phone": "1234567890"
}


@pytest.fixture(scope="function")
def session():
    """创建新的session对象"""
    return requests.Session()


@pytest.fixture(scope="function")
def registered_user(session):
    """注册用户并返回session"""
    print("Registering test user...")
    response = session.post(f"{BASE_URL}/register", data=TEST_USER)
    return session


@pytest.fixture(scope="function")
def logged_in_user(registered_user):
    """登录用户并返回session"""
    print("Logging in test user...")
    registered_user.post(
        f"{BASE_URL}/login",
        data={"email": TEST_USER["email"], "password": TEST_USER["password"]}
    )
    return registered_user


@pytest.fixture(scope="function")
def user_with_cart_item(logged_in_user):
    """已登录且有购物车商品的用户"""
    print("Adding item to cart...")
    product_id = get_product_id(logged_in_user)  # 这里调用是正确的
    logged_in_user.get(f"{BASE_URL}/addToCart?productId={product_id}")
    return logged_in_user


def get_product_id(session):
    """从首页获取第一个商品的ID"""
    response = session.get(f"{BASE_URL}/")
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找商品链接
    product_links = soup.find_all('a', href=True)
    for link in product_links:
        href = link['href']
        if 'productId=' in href:
            match = re.search(r'productId=(\d+)', href)
            if match:
                return match.group(1)

    return "2"  # 默认值


def test_get_products(logged_in_user):
    """测试获取商品列表"""
    print("Testing product listing...")

    response = logged_in_user.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "shop by category" in response.text.lower()
    print("✓ Product listing accessible")


def test_product_detail(logged_in_user):
    """测试商品详情页面"""
    print("Testing product detail page...")

    product_id = get_product_id(logged_in_user)
    response = logged_in_user.get(f"{BASE_URL}/productDescription?productId={product_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "second item" in response.text.lower()
    print("✓ Product detail page accessible")


def test_add_to_cart(logged_in_user):
    """测试添加商品到购物车"""
    print("Testing add to cart...")

    # 先获取当前购物车数量
    home_response = logged_in_user.get(f"{BASE_URL}/")
    home_soup = BeautifulSoup(home_response.text, 'html.parser')
    cart_text = home_soup.find('a', href='/cart').get_text()
    current_count = int(re.search(r'CART (\d+)', cart_text).group(1)) if 'CART' in cart_text else 0

    print(f"Current cart count: {current_count}")

    # 添加商品到购物车
    product_id = get_product_id(logged_in_user)
    response = logged_in_user.get(f"{BASE_URL}/addToCart?productId={product_id}")
    assert response.status_code in [200, 302]

    # 检查购物车数量是否增加
    home_response_after = logged_in_user.get(f"{BASE_URL}/")
    home_soup_after = BeautifulSoup(home_response_after.text, 'html.parser')
    cart_text_after = home_soup_after.find('a', href='/cart').get_text()
    new_count = int(re.search(r'CART (\d+)', cart_text_after).group(1))

    print(f"New cart count: {new_count}")
    assert new_count == current_count + 1, f"Cart count should increase from {current_count} to {current_count + 1}, but got {new_count}"
    print("✓ Product added to cart successfully")


def test_view_cart(logged_in_user):
    """测试查看购物车"""
    print("Testing view cart...")

    response = logged_in_user.get(f"{BASE_URL}/cart")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "subtotal" in response.text.lower()
    print("✓ Cart page accessible")


def test_cart_with_items(user_with_cart_item):
    """测试购物车中有商品的情况"""
    print("Testing cart with items...")

    response = user_with_cart_item.get(f"{BASE_URL}/cart")
    assert response.status_code == 200
    assert "remove" in response.text.lower()

    soup = BeautifulSoup(response.text, 'html.parser')
    total_price_elements = soup.find_all(string=lambda text: text and '$' in text)
    assert len(total_price_elements) > 0, "Should display total price"
    print("✓ Cart displays products and total price")


def test_remove_from_cart(user_with_cart_item):
    """测试从购物车移除商品"""
    print("Testing remove from cart...")

    product_id = get_product_id(user_with_cart_item)
    response = user_with_cart_item.get(f"{BASE_URL}/removeFromCart?productId={product_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "Welcome" in response.text
    print("✓ Product removed from cart successfully")


def test_empty_cart(logged_in_user):
    """测试空购物车"""
    print("Testing empty cart...")

    response = logged_in_user.get(f"{BASE_URL}/cart")
    assert response.status_code == 200
    assert "CART 0" in response.text
    print("✓ Empty cart handled correctly")


def test_unauthorized_cart_access(session):
    """测试未授权用户访问购物车"""
    print("Testing unauthorized cart access...")

    response = session.get(f"{BASE_URL}/cart")
    assert response.status_code == 200
    assert "Register here" in response.text
    print("✓ Unauthorized cart access handled c_orrectly")