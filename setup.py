"""A setuptools based setup module for pm-utils"""


from os import path
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))
NAME = "pm_utils"

# Load the version
with open(path.join(HERE, NAME, "version.py")) as version_file:
    exec(version_file.read())

# Get the long description from the README file
with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

REQUIREMENTS = [
    "pandas",
]

# TODO
TEST_REQUIREMENTS = [
]

# TODO
SETUP_REQUIREMENTS = [
]

setup(
    name=NAME,
    version=__version__,
    description="Utilities for project managers",
    long_description=LONG_DESCRIPTION,
    long_description_type= "text/markdown",
    # applicable after transferring this repo to BCM-HGSC private
    author="Baylor College of Medicine - Human Genome Sequencing Center",
    author_email="questions@hgsc.bcm.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=REQUIREMENTS,
    tests_requires=TEST_REQUIREMENTS,
    setup_requires=SETUP_REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "project_averages.py=pm-utils.project_averages:main",
            "report_90x.py=pm-utils.report_90x:main",
            "report_merged_qc_results.py=pm-utils.report_merged_qc_results:main",
            "report_se.py=pm-utils.report_se:main",
        ],
    },
)

