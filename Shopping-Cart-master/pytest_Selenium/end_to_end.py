import pytest
import time
from Pages.HomePage import HomePage
from Pages.LoginPage import LoginPage
from Pages.RegisterPage import RegisterPage
from Pages.ProductPage import ProductPage
from Pages.CartPage import CartPage
from Pages.ProfilePage import ProfilePage, EditProfilePage


class TestECommerceE2E:
    @pytest.fixture(autouse=True)
    def setup(self, browser, app_url):
        self.driver = browser
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

        # 登录
        login_page = LoginPage(self.driver)
        login_page.login('testuser@example.com', 'testpassword')

        # 验证登录成功
        assert self.home_page.is_user_logged_in()

    def test_browse_products_and_add_to_cart(self):
        """测试浏览商品和添加到购物车"""
        # 先登录
        self._login()

        # 浏览商品并添加到购物车
        self.home_page.click_first_product()

        product_page = ProductPage(self.driver)
        product_name = product_page.get_product_name()
        product_page.add_to_cart()

        # 查看购物车
        self.home_page.click_cart()
        cart_page = CartPage(self.driver)

        # 验证购物车中有商品
        assert cart_page.get_cart_items_count() > 0
        assert product_name in cart_page.get_item_names()

    def test_remove_from_cart(self):
        """测试从购物车移除商品"""
        # 先登录并添加商品到购物车
        self._login()
        self._add_product_to_cart()

        # 转到购物车
        self.home_page.click_cart()
        cart_page = CartPage(self.driver)

        # 记录初始商品数量
        initial_items = cart_page.get_cart_items_count()

        # 移除商品
        if initial_items > 0:
            cart_page.remove_first_item()
            time.sleep(2)  # 等待页面刷新

            # 验证商品被移除
            final_items = cart_page.get_cart_items_count()
            assert final_items < initial_items

    def test_user_logout(self):
        """测试用户登出"""
        # 先登录
        self._login()

        # 登出
        self.home_page.click_logout()

        # 验证登出成功
        assert self.home_page.is_element_present(HomePage.LOGIN_LINK)

    def test_invalid_login(self):
        """测试无效登录"""
        # 导航到登录页面
        self.home_page.click_login()
        login_page = LoginPage(self.driver)

        # 输入无效凭据
        login_page.login('invalid@example.com', 'wrongpassword')

        # 验证显示错误消息
        error_message = login_page.get_error_message()
        assert error_message != ""

    def test_empty_cart_checkout(self):
        """测试空购物车"""
        # 先登录
        self._login()

        # 转到购物车
        self.home_page.click_cart()
        cart_page = CartPage(self.driver)

        # 如果是空购物车，验证显示空购物车消息
        if cart_page.get_cart_items_count() == 0:
            empty_msg = cart_page.get_empty_cart_message().lower()
            assert "empty" in empty_msg or "no items" in empty_msg

    def test_user_profile_management(self):
        """测试用户资料管理"""
        # 先登录
        self._login()

        # 转到个人资料
        self.home_page.click_my_account()
        self.home_page.click_profile()

        profile_page = ProfilePage(self.driver)
        profile_page.click_edit_profile()

        # 更新资料
        edit_profile_page = EditProfilePage(self.driver)
        edit_profile_page.update_city("New Test City")

        # 验证更新成功（根据实际应用调整）
        success_msg = edit_profile_page.get_success_message()
        assert success_msg != ""

    # 辅助方法
    def _login(self):
        """登录辅助方法"""
        if not self.home_page.is_user_logged_in():
            self.home_page.click_login()
            login_page = LoginPage(self.driver)
            login_page.login('testuser@example.com', 'testpassword')
            assert self.home_page.is_user_logged_in()

    def _add_product_to_cart(self):
        """添加商品到购物车辅助方法"""
        self.home_page.click_first_product()
        product_page = ProductPage(self.driver)
        product_page.add_to_cart()
        # 返回首页继续操作
        self.driver.get("http://localhost:5000")