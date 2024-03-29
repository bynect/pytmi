from setuptools import setup, find_packages
from pytmi import __version__ as version


description = """TMI (Twitch Messaging Interface) library for Python."""


project_url = "https://github.com/bynect/pytmi"


classifiers = [
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]


with open("README.md") as f:
    readme = f.read()


setup_info = {
    "name": "pytmi",
    "version": version,
    "author": "nect",
    "description": description,
    "long_description": readme,
    "long_description_content_type": "text/markdown",
    "url": project_url,
    "packages": find_packages(),
    "classifiers": classifiers,
    "python_requires": ">= 3.7",
}


setup(**setup_info)
