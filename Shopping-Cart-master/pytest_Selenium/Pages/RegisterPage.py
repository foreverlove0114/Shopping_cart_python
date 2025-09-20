# Pages/HomePage.py
from .BasePage import BasePage  # ✅ 正确：相对导入
from selenium.webdriver.common.by import By


class RegisterPage(BasePage):
    # Locators based on register.html
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    CONFIRM_PASSWORD_INPUT = (By.NAME, "cpassword")
    FIRSTNAME_INPUT = (By.NAME, "firstName")
    LASTNAME_INPUT = (By.NAME, "lastName")
    ADDRESS1_INPUT = (By.NAME, "address1")
    ADDRESS2_INPUT = (By.NAME, "address2")
    ZIPCODE_INPUT = (By.NAME, "zipcode")
    CITY_INPUT = (By.NAME, "city")
    STATE_INPUT = (By.NAME, "state")
    COUNTRY_INPUT = (By.NAME, "country")
    PHONE_INPUT = (By.NAME, "phone")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "input[type='submit']")
    LOGIN_LINK = (By.LINK_TEXT, "Login here")

    def __init__(self, driver):
        super().__init__(driver)

    # RegisterPage.py
    def register_user(self, user_data):
        """注册用户"""
        try:
            # 逐个字段填写
            self.send_keys(self.EMAIL_INPUT, user_data['email'])
            self.send_keys(self.PASSWORD_INPUT, user_data['password'])
            self.send_keys(self.CONFIRM_PASSWORD_INPUT, user_data['password'])
            self.send_keys(self.FIRSTNAME_INPUT, user_data['firstName'])
            self.send_keys(self.LASTNAME_INPUT, user_data['lastName'])
            self.send_keys(self.ADDRESS1_INPUT, user_data['address1'])
            self.send_keys(self.ADDRESS2_INPUT, user_data.get('address2', ''))
            self.send_keys(self.ZIPCODE_INPUT, user_data['zipcode'])
            self.send_keys(self.CITY_INPUT, user_data['city'])
            self.send_keys(self.STATE_INPUT, user_data['state'])
            self.send_keys(self.COUNTRY_INPUT, user_data['country'])
            self.send_keys(self.PHONE_INPUT, user_data['phone'])

            # 提交表单
            self.click_submit()

        except Exception as e:
            print(f"注册过程中出错: {e}")
            raise

    def click_submit(self):
        self.click_element(self.SUBMIT_BUTTON)

    def click_login_link(self):
        self.click_element(self.LOGIN_LINK)