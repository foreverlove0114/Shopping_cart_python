# Pages/HomePage.py
from .BasePage import BasePage  # ✅ 正确：相对导入
from selenium.webdriver.common.by import By

class HomePage(BasePage):
    # Locators
    LOGIN_LINK = (By.LINK_TEXT, "Sign In")
    LOGOUT_LINK = (By.LINK_TEXT, "Sign Out")
    CART_LINK = (By.XPATH, "//*[@id='kart']/a")
    MY_ACCOUNT_DROPDOWN = (By.CLASS_NAME, "dropbtn")
    PROFILE_LINK = (By.LINK_TEXT, "Your profile")
    PRODUCT_LINKS = (By.XPATH, "//tr[@id='productImage']//a")
    # CATEGORY_LINKS = (By.CSS_SELECTOR, ".displayCategory a")
    WELCOME_MESSAGE = (By.CLASS_NAME, "dropbtn")

    def __init__(self,driver):
        super().__init__(driver)

    def click_login(self):
        self.click_element(self.LOGIN_LINK)

    def click_logout(self):
        self.click_element(self.LOGOUT_LINK)

    def click_cart(self):
        self.click_element(self.CART_LINK)

    def click_my_account(self):
        self.click_element(self.MY_ACCOUNT_DROPDOWN)

    def click_profile(self):
        self.click_element(self.PROFILE_LINK)

    def get_first_product(self):
        products = self.find_elements(self.PRODUCT_LINKS)
        return products[0] if products else None

    def click_first_product(self):
        product = self.get_first_product()
        if product:
            product.click()

    def is_user_logged_in(self):
        return self.is_element_present(self.LOGOUT_LINK)

    def get_welcome_message(self):
        return self.get_text(self.WELCOME_MESSAGE)













