#encoding: utf-8
from setuptools import setup, find_packages
import lightapi

setup(
	name = "django-lightapi",
    version = lightapi.get_version(),
    description = "django-lightapi is a super light weight api framework for exposing restful django webservices",
    author = "Úlfur Kristjánsson",
    author_email = "ulfur@theawesometastic.com",
    url = "https://github.com/ulfur/django-lightapi",
    packages = find_packages( ),
	include_package_data=True
)
