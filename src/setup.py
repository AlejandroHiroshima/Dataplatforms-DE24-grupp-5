from setuptools import setup
from setuptools import find_packages

# find_packages will find all the packages with init.py
print(find_packages())

setup(
    name="coins_project",
    version="0.0.1",
    description="""test package install""",
    author="Ghost",
    author_email="YOUR_EMAIL@mail.com",
    install_requires=[],
    packages=find_packages(exclude=("explorations")),
    # entry_points={"console_scripts": ["dashboard = utils.run_dashboard:run_dashboard"]},
)
