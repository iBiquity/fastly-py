import sys
from setuptools import setup, find_packages

exec (open('fastly/_version.py').read())

install_requires = [] if sys.version_info[0] < 3 else [
    'asyncio',
    'aiohttp',
]

setup(
    name="fastly",
    version=__version__,
    author="Fastly",
    author_email="support@fastly.com",
    description="Fastly python API",
    keywords="fastly api",
    url="https://github.com/fastly/fastly-py",
    packages=['fastly']+['fastly.' + i
                          for i in find_packages(where = './fastly')],
    long_description=open('README.md').read(),
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"
    ],
    install_requires=install_requires,
    scripts=[
        "bin/purge_service",
        "bin/purge_key",
        "bin/purge_url"
    ]
)
