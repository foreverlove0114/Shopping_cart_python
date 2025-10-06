from http.client import responses
import os
import pytest
import requests
from bs4 import BeautifulSoup

# 从环境变量读取BASE_URL，支持Jenkins参数化
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
def test_user_edited():
    """为每个测试提供独立的测试数据"""
    return {
        "firstName": "JieXiang",
        "lastName": "Yu",
        "address1": "Yong",
        "address2": "Peng",
        "zipcode": "83700",
        "city": "Yong Peng",
        "state": "Johor",
        "country": "Malaysia",
        "phone": "011101111"
    }


@pytest.fixture(scope="function")
def session():
    """创建共享的session对象"""
    return requests.Session()

@pytest.fixture(scope="function")
def registered_user(session):
    """注册用户并返回session，不包含断言"""
    print("Registering test user...")
    session.post(f"{BASE_URL}/register", data=TEST_USER)
    return session


@pytest.fixture(scope="function")
def logged_in_user(registered_user):
    """登录用户并返回session，不包含断言"""
    print("Logging in test user...")
    registered_user.post(
        f"{BASE_URL}/login",
        data={"email": TEST_USER["email"], "password": TEST_USER["password"]}
    )
    return registered_user

@pytest.fixture(scope="function")
def account_with_editprofile(logged_in_user):
    """进入profile页面并返回session，不包含断言"""
    print("Entering edit profile page...")
    logged_in_user.get(f"{BASE_URL}/account/profile/edit")
    return logged_in_user


def test_register_user(session):
    """测试用户注册功能"""
    print(f"🌐 测试环境: {BASE_URL}")

    response = session.post(
        f"{BASE_URL}/register",  # 使用环境变量
        data=TEST_USER
    )

    # 注册应该成功（200表示显示成功页面，302表示重定向）
    assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"

    # 检查响应中是否包含成功消息
    if response.status_code == 200:
        assert "Registered Successfully" in response.text
        print("✓ User registered successfully with success message")


def test_login_success(registered_user):
    """测试成功登录"""
    print("Testing successful login...")

    response = registered_user.post(
        f"{BASE_URL}/login",
        data={"email":TEST_USER["email"],"password":TEST_USER["password"]}
    )

    assert response.status_code == 200, f"Expected 200, got{response.status_code}"
    assert "session" in registered_user.cookies, "Session cookie should be set after login"
    print("✓ Login successful, session cookie set")


def test_login_failure(registered_user):
    """测试登录失败情况"""
    print("Testing login failure...")

    response = registered_user.post(
        f"{BASE_URL}/login",
        data={"email":TEST_USER["email"],"password":"wrongpassword"}
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "Invalid" in response.text, "Should show invalid credentials message"
    assert "session" not in registered_user.cookies
    print("✓ Login failure handled correctly")


def test_logout(logged_in_user):
    """测试用户登出"""
    print("Testing logout...")
    print(f"Before logout - Session cookies: {dict(logged_in_user.cookies)}")

    response = logged_in_user.get(f"{BASE_URL}/logout")

    print(f"After logout - Status: {response.status_code}, Cookies: {dict(logged_in_user.cookies)}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # 检查session cookie是否被清除
    assert "session" not in logged_in_user.cookies
    print("✓ Logout successful")

def test_profile_access(logged_in_user):
    """测试个人资料页面访问"""
    print("Testing profile access...")

    response = logged_in_user.get(f"{BASE_URL}/account/profile")

    assert response.status_code == 200, f"Expected 200, git {response.status_code}"
    assert "View Profile" in response.text
    print("✓ Profile edit page accessible")

def test_profile_edit(logged_in_user):
    """测试个人资料编辑页面"""
    print("Testing profile edit page...")

    response = logged_in_user.get(f"{BASE_URL}/account/profile/edit")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "Save" in response.text
    print("✓ Profile edit page accessible")

def test_unauthorized_access(session):
    """测试未授权访问保护页面"""
    print("Testing unauthorized access...")

    response = session.get(f"{BASE_URL}/account/profile")
    assert response.status_code == 200, f"Expected redirect, got {response.status_code}"
    assert "<title>Welcome</title>" in response.text
    print("✓ Unauthorized access redirected correctly")

def test_update_profile(account_with_editprofile):
    # 构建测试数据
    test_data = {
        "email": "testuser@example.com",
        "firstName": "JieXiang",
        "lastName": "Yu2",
        "address1": "Yong1",
        "address2": "Peng1",
        "zipcode": "8370",
        "city": "kuala lumpur",
        "state": "Johor",
        "country": "Malaysia5",
        "phone": "0111011112"
    }

    # 执行更新
    update_response = account_with_editprofile.post(
        f"{BASE_URL}/updateProfile", data=test_data
    )
    print(f"Update status: {update_response.status_code}")

    # 获取更新后的数据
    after_response = account_with_editprofile.get(f"{BASE_URL}/account/profile/edit")
    after_soup = BeautifulSoup(after_response.text, 'html.parser')

    # 断言验证
    assert after_soup.find('input', {'name': 'firstName'}).get('value') == "JieXiang"
    assert after_soup.find('input', {'name': 'lastName'}).get('value') == "Yu2"
    assert after_soup.find('input', {'name': 'address1'}).get('value') == "Yong1"
    assert after_soup.find('input', {'name': 'address2'}).get('value') == "Peng1"
    assert after_soup.find('input', {'name': 'zipcode'}).get('value') == "8370"
    assert after_soup.find('input', {'name': 'city'}).get('value') == "kuala lumpur"
    assert after_soup.find('input', {'name': 'state'}).get('value') == "Johor"
    assert after_soup.find('input', {'name': 'country'}).get('value') == "Malaysia5"
    assert after_soup.find('input', {'name': 'phone'}).get('value') == "0111011112"

    print("✓ Profile update test completed successfully!")













