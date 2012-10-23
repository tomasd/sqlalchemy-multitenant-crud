from setuptools import setup, find_packages


setup(
    name='sqlalchemy-crud',
    version='',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url='',
    license='',
    author='Tomas Drencak',
    author_email='tomas@drencak.com',
    description='',
    install_requires=['sqlalchemy'],
    tests_require=['nose']
)
