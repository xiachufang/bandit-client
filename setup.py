# coding: utf-8
from __future__ import absolute_import

from setuptools import find_packages, setup


setup(
    name='bandit_client',
    version='0.2.0',
    keywords=('bandit client',),
    description='bandit client',
    license='MIT License',
    install_requires=['simplejson', 'requests', 'six'],
    author='Yana, GUOQIANG LIN',
    author_email='yangyang@xiachufang.com, linguoqiang@xiachufang.com',

    packages=find_packages(exclude=['*.md', '*.yml', '*.pyc']),
    platforms='any',

    url='https://github.com/xiachufang/bandit-client',
    include_package_data=True,

)
