# coding: utf-8
from setuptools import setup, find_packages

setup(
    name='bandit-client',

    version='0.0.1',

    description='The client of bandit-server',
    long_description='The client of bandit-server use in xiachufang',

    url='https://github.com/xiachufang/bandit-client',

    # Author details
    author='yangyang',
    author_email='yangyang@xiachufang.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['requests', ],
    keywords='click adjust',
    include_package_data=True
)