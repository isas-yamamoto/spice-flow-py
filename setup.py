import pathlib
import re
import sys

from setuptools import find_packages, setup

root = pathlib.Path(__file__).parent
version_text = (root / "spiceflow" / "version.py").read_text(encoding="utf-8")
match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', version_text)
if not match:
    raise RuntimeError("Could not read __version__ from spiceflow/version.py")
__version__ = match.group(1)

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

info = sys.version_info

setup(
    name="spice-flow",
    version=__version__,
    description="Field of view visualizer using SPICE",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Yukio Yamamoto",
    author_email="yukio@planeta.sci.isas.jaxa.jp",
    url="https://github.com/isas-yamamoto/spice-flow-py",
    packages=find_packages(),
    include_package_data=True,
    keywords="SPICE",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    test_suite="test",
)
