import sys
from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()


info = sys.version_info

setup(
    name="spice-flow",
    version="0.0.0.1",
    description="Field of view visuallizer using SPICE",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Yukio Yamamoto",
    author_email="yukio@planeta.sci.isas.jaxa.jp",
    url="https://github.com/isas-yamamoto/spice-flow-py",
    packages=find_packages(),
    include_package_data=True,
    keywords="SPICE",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    test_suite="test",
)
