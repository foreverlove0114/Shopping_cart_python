import pytest
import time
from Pages.HomePage import HomePage
from Pages.LoginPage import LoginPage
from Pages.RegisterPage import RegisterPage
from Pages.ProductPage import ProductPage
from Pages.CartPage import CartPage
from Pages.ProfilePage import ProfilePage, EditProfilePage
from selenium.webdriver.common.by import By
import os


class TestECommerceE2E:
    @pytest.fixture(autouse=True)
    def setup(self, browser):
        self.driver = browser
        # 从环境变量读取BASE_URL
        app_url = os.getenv('BASE_URL', 'http://localhost:5000')
        self.driver.get(app_url)
        self.home_page = HomePage(self.driver)
        yield

    def test_home_page_loads(self):
        """测试首页加载"""
        assert "Welcome" in self.driver.title
        assert self.home_page.is_element_present(HomePage.LOGIN_LINK)

    def test_user_registration_and_login(self):
        """测试用户注册和登录流程"""
        # 导航到注册页面
        self.home_page.click_login()
        login_page = LoginPage(self.driver)
        login_page.click_register()

        # 填写注册表单
        register_page = RegisterPage(self.driver)
        user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'firstName': 'Test',
            'lastName': 'User',
            'address1': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'country': 'Testland',
            'phone': '1234567890',
            'zipcode': '12345'
        }
        register_page.register_user(user_data)
        time.sleep(1)

        # 登录
        login_page = LoginPage(self.driver)
        login_page.login('testuser@example.com', 'testpassword')

        # 验证登录成功
        assert self.home_page.is_user_logged_in()

    def test_browse_products_and_add_to_cart(self):
        self._login()
        time.sleep(1)

        # 获取首页的商品信息
        first_product = self.home_page.get_first_product()
        if not first_product:
            print("❌ 首页没有商品")
            return

        print(f"🛍️ 选择商品: {first_product.text}")
        first_product.click()
        time.sleep(1)

        # 获取商品详情
        product_page = ProductPage(self.driver)
        product_name = product_page.get_product_name()
        print(f"➕ 添加商品到购物车: {product_name}")
        product_page.add_to_cart()
        time.sleep(1)

        # 直接查看购物车
        self.driver.get("http://localhost:5000/cart")
        time.sleep(1)

        # 检查购物车状态
        cart_page = CartPage(self.driver)
        item_count = cart_page.get_cart_items_count()
        if item_count == 0:
            print("❌ 购物车为空，测试失败")
            assert False, "商品未成功添加到购物车"
        else:
            print(f"✅ 购物车中有 {item_count} 件商品")
            assert True

    def test_remove_from_cart(self):
        self._login()
        self._add_product_to_cart()

        # 转到购物车
        self.driver.get("http://localhost:5000/cart")
        time.sleep(1)
        cart_page = CartPage(self.driver)

        # 记录初始商品数量
        initial_items = cart_page.get_cart_items_count()
        # 移除商品
        if initial_items > 0:
            cart_page.remove_first_item()
            time.sleep(1)

        # 验证商品被移除
        self.driver.get("http://localhost:5000/cart")
        time.sleep(1)
        final_items = cart_page.get_cart_items_count()
        assert final_items<initial_items

    def test_user_logout(self):
        self._login()

        self.home_page.click_my_account()
        self.home_page.click_logout()

        assert self.home_page.is_element_present(HomePage.LOGIN_LINK)

    def test_invalid_login(self):
        self.home_page.click_login()
        login_page = LoginPage(self.driver)

        login_page.login('invalid@example.com', 'wrongpassword')

        error_message = login_page.get_error_message()
        assert error_message == "Invalid UserId / Password"

    def test_empty_cart_checkout(self):
        self._login()
        time.sleep(1)

        cart_page = CartPage(self.driver)
        self.driver.get("http://localhost:5000/cart")
        time.sleep(1)

        # 如果是空购物车，验证显示空购物车消息
        assert cart_page.get_cart_items_count() == 0

    def test_user_profile_management(self):
        self._login()

        self.home_page.click_my_account()
        self.home_page.click_profile()
        time.sleep(1)

        profile_page = ProfilePage(self.driver)
        profile_page.click_edit_profile()

        edit_profile_page = EditProfilePage(self.driver)
        edit_profile_page.update_city("New Test City")

        time.sleep(1)
        self.driver.get("http://localhost:5000/account/profile/edit")

    #==================================================================
    # 辅助方法
    # =================================================================
    def _login(self):
        if not self.home_page.is_user_logged_in():
            self.home_page.click_login()
            login_page = LoginPage(self.driver)
            login_page.login('jiexiang01144@gmail.com', 'JXiang29')

    def _add_product_to_cart(self):
        self.home_page.click_first_product()
        product_page = ProductPage(self.driver)
        product_page.add_to_cart()
        # 返回首页继续操作
        self.driver.get("http://localhost:5000")

