from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requirements = [
    "bg-atlasapi",
    "bg-space",
    "numpy",
    "configparser",
    "scikit-image",
    "multiprocessing-logging",
    "configobj",
    "slurmio",
    "imio",
    "fancylog",
    "imlib>=0.0.26",
]


setup(
    name="brainreg",
    version="0.4.0-rc0",
    description="Automated 3D brain registration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "napari": [
            "napari[pyside2]",
            "brainglobe-napari-io",
            "brainreg-segment>=0.0.2",
        ],
        "dev": [
            "black",
            "pytest-cov",
            "pytest",
            "coverage",
            "bump2version",
            "pre-commit",
            "flake8",
        ],
    },
    python_requires=">=3.7",
    packages=find_packages(),
    entry_points={"console_scripts": ["brainreg = brainreg.cli:main"]},
    include_package_data=True,
    author="Adam Tyson, Charly Rousseau",
    author_email="code@adamltyson.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)
