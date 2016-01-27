from setuptools import setup

VERSION = '0.0.1'

setup(
    name='pymarketo',
    version=VERSION,
    packages=['pymarketo'],
    install_requires=[
        'requests>=2.8.1',
        'six'
        ],

    description='Python interface to the Marketo REST API',
    author='Jeremy Swinarton',
    author_email='jeremy@swinarton.com',
    license='MIT',
)
