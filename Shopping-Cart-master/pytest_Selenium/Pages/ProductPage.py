# Pages/HomePage.py
from .BasePage import BasePage  # ✅ 正确：相对导入
from selenium.webdriver.common.by import By


class ProductPage(BasePage):
    # Locators based on productDescription.html
    ADD_TO_CART_BUTTON = (By.LINK_TEXT, "Add to Cart")
    PRODUCT_NAME = (By.TAG_NAME, "h1")
    PRODUCT_PRICE = (By.XPATH, "//td[text()='Price']/following-sibling::td")
    PRODUCT_DESCRIPTION = (By.TAG_NAME, "p")
    PRODUCT_IMAGE = (By.ID, "productImage")

    def __init__(self, driver):
        super().__init__(driver)

    def add_to_cart(self):
        self.click_element(self.ADD_TO_CART_BUTTON)

    def get_product_name(self):
        return self.get_text(self.PRODUCT_NAME)

    def get_product_price(self):
        return self.get_text(self.PRODUCT_PRICE)

    def get_product_description(self):
        return self.get_text(self.PRODUCT_DESCRIPTION)