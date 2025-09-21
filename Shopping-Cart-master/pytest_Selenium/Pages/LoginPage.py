# Pages/HomePage.py
from .BasePage import BasePage  # ✅ 正确：相对导入
from selenium.webdriver.common.by import By

class LoginPage(BasePage):
    # Locators based on login.html
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "input[type='submit']")
    ERROR_MESSAGE = (By.XPATH, "//p[contains(text(), 'Invalid') or contains(text(), 'error')]")
    REGISTER_LINK = (By.LINK_TEXT, "Register here")

    def __init__(self,driver):
        super().__init__(driver)

    def enter_email(self,email):
        self.send_keys(self.EMAIL_INPUT,email)

    def enter_password(self,password):
        self.send_keys(self.PASSWORD_INPUT,password)

    def click_submit(self):
        self.click_element(self.SUBMIT_BUTTON)

    def click_register(self):
        self.click_element(self.REGISTER_LINK)

    def login(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.click_submit()

    def get_error_message(self):
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except:
            return ""

















