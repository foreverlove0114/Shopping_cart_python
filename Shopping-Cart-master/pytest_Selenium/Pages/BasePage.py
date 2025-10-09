import time

from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    """
    页面对象模型(POM)的基类
    封装了Selenium WebDriver的常用操作，提供统一的页面交互方法
    所有具体页面类都应该继承这个基类
    """

    def __init__(self,driver):
        """
        初始化BasePage

        Args:
            driver: Selenium WebDriver实例，用于浏览器操作
        """
        self.driver = driver
        # 创建显式等待对象，设置超时时间为10秒
        self.wait = WebDriverWait(driver,10)

    def find_element(self,locator):
        """
        查找单个页面元素（使用显式等待）

        Args:
            locator: 元素定位器，格式为 (By.策略, '定位表达式')
                    例如：(By.ID, 'username'), (By.XPATH, '//button[@type="submit"]')

        Returns:
            WebElement: 找到的页面元素对象

        Raises:
            TimeoutException: 如果在超时时间内未找到元素
        """
        # 等待元素出现在DOM中（不一定可见或可点击）
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self,locator):
        """
        查找多个页面元素（使用显式等待）

        Args:
            locator: 元素定位器

        Returns:
            list: 包含所有找到的WebElement对象的列表

        Raises:
            TimeoutException: 如果在超时时间内未找到任何元素
        """
        # 等待至少一个元素出现在DOM中
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click_element(self,locator):
        """
        点击页面元素

        Args:
            locator: 元素定位器

        Raises:
            TimeoutException: 如果在超时时间内元素不可点击
        """
        # 等待元素可点击（可见且启用状态）
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def send_keys(self,locator,text):
        """
        向输入框输入文本

        Args:
            locator: 输入框元素定位器
            text: 要输入的文本内容

        步骤：
        1. 找到元素
        2. 清空现有内容
        3. 等待1秒（确保清空操作完成）
        4. 输入新文本
        """
        element = self.find_element(locator)
        element.clear()
        time.sleep(1)
        element.send_keys(text)

    def get_text(self,locator):
        """
        获取元素的文本内容

        Args:
            locator: 元素定位器

        Returns:
            str: 元素的文本内容
        """
        return self.find_element(locator).text

    def is_element_present(self,locator):
        """
        检查元素是否存在于页面中

        Args:
            locator: 元素定位器

        Returns:
            bool: 如果元素存在返回True，否则返回False

        注意：这个方法不会抛出异常，适合用于断言或条件判断
        """
        try:
            self.find_element(locator)
            return True
        except TimeoutException:
            return False