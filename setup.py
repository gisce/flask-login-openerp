from setuptools import setup, find_packages


setup(
    name='flask-login-openerp',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/gisce/flask-login-openerp',
    license='MIT',
    author='GISCE-TI, S.L.',
    install_requires=['Flask', 'Flask-Login', 'Flask-OpenERP', 'Flask-WTF'],
    include_package_data=True,
    author_email='ti@gisce.net',
    description='OpenERP Login for Flask using Flask-Login'
)
