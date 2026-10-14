from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in fhc_visitor_management/__init__.py
from fhc_visitor_management import __version__ as version

setup(
    name="fhc_visitor_management",
    version=version,
    description="Federal Housing Corporation - Visitor Management System",
    author="Federal Housing Corporation",
    author_email="it@fhc.gov.ng",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
