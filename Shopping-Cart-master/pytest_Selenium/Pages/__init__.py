# Pages/__init__.py
from .BasePage import BasePage
from .HomePage import HomePage
from .LoginPage import LoginPage
from .RegisterPage import RegisterPage
from .ProductPage import ProductPage
from .CartPage import CartPage
from .ProfilePage import ProfilePage, EditProfilePage

__all__ = [
    'BasePage',
    'HomePage',
    'LoginPage',
    'RegisterPage',
    'ProductPage',
    'CartPage',
    'ProfilePage',
    'EditProfilePage'
]