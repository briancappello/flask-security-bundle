from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask Security Bundle',
    version='0.1.2',
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
        'flask-controller-bundle>=0.2.0',
        'flask-mail-bundle>=0.2.0',
        'flask-security>=3.0.0',
        'flask-sqlalchemy-bundle>=0.2.0',
        'flask-unchained>=0.2.0',
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
