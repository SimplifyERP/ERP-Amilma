from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in amilma_custom/__init__.py
from amilma_custom import __version__ as version

setup(
	name="amilma_custom",
	version=version,
	description="Custom Development",
	author="Vivek",
	author_email="vivekchamp84@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
