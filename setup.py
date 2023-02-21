from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requirements = [
    "bg-atlasapi",
    "bg-space",
    "fancylog",
    "imio",
    "imlib>=0.0.26",
    "numpy",
    "scikit-image",
]


setup(
    name="brainreg",
    version="0.4.0",
    description="Automated 3D brain registration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "napari": [
            "napari[pyside2]",
            "brainreg-napari",
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
    python_requires=">=3.8",
    package_dir={"": "src"},
    entry_points={"console_scripts": ["brainreg = brainreg.cli:main"]},
    include_package_data=True,
    author="Adam Tyson, Charly Rousseau",
    author_email="code@adamltyson.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)
