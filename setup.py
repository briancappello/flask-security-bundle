from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask Security Bundle',
    version='0.3.0',
    description='Authentication and authorization support for Flask Unchained',
    long_description=long_description,
    url='https://github.com/briancappello/flask-security-bundle',
    author='Brian Cappello',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'bcrypt>=3.1.3',
        'blinker>=1.4',
        'flask>=0.12.2',
        'flask-babelex>=0.9.3',
        'flask-login>=0.3.0',
        'flask-principal>=0.3.3',
        'flask-unchained>=0.5.1',
        'flask-wtf>=0.13.1',
        'itsdangerous>=0.21',
        'passlib>=1.7',
    ],
    extras_require={
        'dev': [
            'coverage',
            'factory_boy',
            'pytest',
            'pytest-flask',
            'tox',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'pytest11': [
            'flask_security_bundle = flask_security_bundle.pytest',
        ],
    },
)
