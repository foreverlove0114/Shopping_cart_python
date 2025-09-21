import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture
def browser():
    """创建浏览器实例"""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(
        service=service,
        options=options
    )
    driver.implicitly_wait(10)

    #driver action
    yield driver

    #teardown
    driver.quit()

@pytest.fixture
def app_url():
    return "http://localhost:5000"

@pytest.fixture
def home_page(browser, app_url):
    """HomePage实例"""
    browser.get(app_url)
    from Pages.HomePage import HomePage
    return HomePage(browser)

@pytest.fixture
def login_page(browser):
    """LoginPage实例"""
    from Pages.LoginPage import LoginPage
    return LoginPage(browser)

@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
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