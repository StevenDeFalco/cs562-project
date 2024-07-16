from setuptools import setup, find_packages


def read_requirements():
    with open('requirements.txt') as requirements_file:
        return requirements_file.read().splitlines()


setup(
    name='ExtendedSQL',
    version='1.0.0',
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'extendedsql=esql:main',
        ],
    },
    author='Lucas Hope',
    author_email='lucasfhope@icloud.com',
    description= (
        "ExtendedSQL is an application interface for a new query language "
        "that allows for computation of aggregates outside of the grouping "
        "variables. This query language is best utilized for OLAP purposes."
    ),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lucasfhope/ExtendedSQL.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)