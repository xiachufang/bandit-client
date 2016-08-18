from setuptools import setup, find_packages

setup(
    name = 'bandit_client',
    version = '0.0.3',
    keywords = ('bandit client'),
    description = 'bandit client',
    license = 'MIT License',
    install_requires = ['simplejson',
                        'requests'],

    author = 'Yana, GUOQIANG LIN',
    author_email = 'yangyang@xiachufang.com, linguoqiang@xiachufang.com',

    packages = find_packages(exclude=['*.md', '*.yml', '*.pyc']),
    platforms = 'any',

    url = 'https://github.com/xiachufang/bandit-client',
    include_package_data = True,

)
