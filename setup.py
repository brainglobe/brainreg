from setuptools import setup, find_namespace_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requirements = [
    "bg-atlasapi==0.0.3rc0",
    "bgspace",
    "numpy>=1.15.4,<1.19.0",
    "configparser",
    "scikit-image>=0.14.0,<0.17.0",
    "multiprocessing-logging",
    "configobj",
    "slurmio",
    "brainio>=0.0.19",
    "fancylog",
    "micrometa",
    "imlib>=0.0.26",
    "neuro>=0.0.13",
]


setup(
    name="brainreg",
    version="0.0.1a",
    description="Automated 3D brain registration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "dev": ["black", "pytest-cov", "pytest", "gitpython", "coverage",]
    },
    python_requires=">=3.6, <3.8",
    packages=find_namespace_packages(exclude=("docs", "tests*")),
    entry_points={"console_scripts": ["brainreg = brainreg.cli:main",]},
    include_package_data=True,
    author="Adam Tyson",
    author_email="adam.tyson@ucl.ac.uk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)