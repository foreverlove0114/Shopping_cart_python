# Pages/HomePage.py
import time

from .BasePage import BasePage  # ✅ 正确：相对导入
from selenium.webdriver.common.by import By


class ProfilePage(BasePage):
    # Locators based on profileHome.html
    EDIT_PROFILE_LINK = (By.LINK_TEXT, "Edit Profile")
    VIEW_PROFILE_LINK = (By.LINK_TEXT, "View Profile")
    CHANGE_PASSWORD_LINK = (By.LINK_TEXT, "Change password")

    def __init__(self, driver):
        super().__init__(driver)

    def click_edit_profile(self):
        self.click_element(self.EDIT_PROFILE_LINK)

    def click_view_profile(self):
        self.click_element(self.VIEW_PROFILE_LINK)

    def click_change_password(self):
        self.click_element(self.CHANGE_PASSWORD_LINK)


class EditProfilePage(BasePage):
    # Locators based on editProfile.html
    CITY_INPUT = (By.NAME, "city")
    FIRSTNAME_INPUT = (By.NAME, "firstName")
    LASTNAME_INPUT = (By.NAME, "lastName")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "input[type='submit']")
    SUCCESS_MESSAGE = (By.XPATH, "//*[contains(text(), 'Success') or contains(text(), 'Saved')]")

    def __init__(self, driver):
        super().__init__(driver)

    def update_city(self, new_city):
        self.send_keys(self.CITY_INPUT, new_city)
        time.sleep(1)
        self.click_submit()

    def update_first_name(self, new_first_name):
        self.send_keys(self.FIRSTNAME_INPUT, new_first_name)

    def update_last_name(self, new_last_name):
        self.send_keys(self.LASTNAME_INPUT, new_last_name)

    def click_submit(self):
        self.click_element(self.SUBMIT_BUTTON)

    def get_success_message(self):
        try:
            return self.get_text(self.SUCCESS_MESSAGE)
        except:
            return ""