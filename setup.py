import setuptools

with open("version.txt", "r") as fh:
    version = fh.read()

with open("README.md", "r") as fh:
    long_description = fh.read()

PACKAGE_NAME = "relax"

setuptools.setup(
    name=PACKAGE_NAME,
    version=version,
    author="ODOUARD Alexandre",
    author_email="odouard.alexandre@mybraintech.com",
    description="InteraX WP3 Relax",
    long_description=long_description,
    url="https://github.com/mbt-alexandre-o/Relax",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',

)