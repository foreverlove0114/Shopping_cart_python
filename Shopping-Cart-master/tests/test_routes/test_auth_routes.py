from http.client import responses

import pytest
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"

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
    """创建共享的session对象"""
    return requests.Session()

def test_register_user(session):
    """测试用户注册功能"""
    print("Testing user registration...")

    response = session.post(
        f"{BASE_URL}/register",
        data=TEST_USER
    )

    # 注册应该成功（200表示显示成功页面，302表示重定向）
    assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"

    # 检查响应中是否包含成功消息
    if response.status_code == 200:
        assert "Registered Successfully" in response.text
        print("✓ User registered successfully with success message")


def test_login_success(session):
    """测试成功登录"""
    print("Testing successful login...")

    response = session.post(
        f"{BASE_URL}/login",
        data={"email":TEST_USER["email"],"password":TEST_USER["password"]}
    )

    assert response.status_code == 200, f"Expected 200, got{response.status_code}"
    assert "session" in session.cookies, "Session cookie should be set after login"
    print("✓ Login successful, session cookie set")


def test_login_failure(session):
    """测试登录失败情况"""
    print("Testing login failure...")

    response = session.post(
        f"{BASE_URL}/login",
        data={"email":TEST_USER["email"],"password":"wrongpassword"}
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "Invalid" in response.text, "Should show invalid credentials message"
    assert "session" not in session.cookies
    print("✓ Login failure handled correctly")


def test_logout(session):
    """测试用户登出"""
    print("Testing logout...")
    print(f"Before logout - Session cookies: {dict(session.cookies)}")

    response = session.get(f"{BASE_URL}/logout")

    print(f"After logout - Status: {response.status_code}, Cookies: {dict(session.cookies)}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # 检查session cookie是否被清除
    assert "session" not in session.cookies
    print("✓ Logout successful")

def test_profile_access(session):
    """测试个人资料页面访问"""
    print("Testing profile access...")

    session.post(
        f"{BASE_URL}/login",
        data={"email":TEST_USER["email"],"password":TEST_USER["password"]}
    )

    response = session.get(f"{BASE_URL}/account/profile")
    assert response.status_code == 200, f"Expected 200, git {response.status_code}"
    assert "View Profile" in response.text
    print("✓ Profile edit page accessible")
