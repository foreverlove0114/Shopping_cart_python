# Pages/HomePage.py
from .BasePage import BasePage  # ✅ 正确：相对导入
from selenium.webdriver.common.by import By


class CartPage(BasePage):
    # Locators based on cart.html
    CART_ITEMS = (By.CSS_SELECTOR, "#tableItems > div")
    REMOVE_BUTTONS = (By.LINK_TEXT, "Remove")
    EMPTY_CART_MESSAGE = (By.XPATH, "//*[@id='kart]/a/text()")
    TOTAL_PRICE = (By.ID, "total")
    CHECKOUT_BUTTON = (By.LINK_TEXT, "Proceed to checkout")
    ITEM_NAMES = (By.ID, "itemNameTag")
    ITEM_PRICES = (By.ID, "itemPrice")
    REMOVE_BUTTON = (By.CSS_SELECTOR, ".remove-btn")
    CART_COUNT = (By.ID, "carticon")

    def __init__(self, driver):
        super().__init__(driver)

    def get_cart_items_count(self):
        return int(len(self.find_elements(self.CART_ITEMS))-1)

    def remove_first_item(self):
        if self.get_cart_items_count() > 0:
            self.click_element(self.REMOVE_BUTTONS)

    def get_empty_cart_message(self):
        try:
            return self.get_text(self.EMPTY_CART_MESSAGE)
        except:
            return ""

    def get_total_price(self):
        return self.get_text(self.TOTAL_PRICE)

    def click_checkout(self):
        self.click_element(self.CHECKOUT_BUTTON)

    def get_item_names(self):
        return [elem.text for elem in self.find_elements(self.ITEM_NAMES)]