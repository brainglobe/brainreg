from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import os
from pathlib import Path
import subprocess
import platform
import glob


class CMakeExtension(Extension):
    def __init__(self, name: str, cmake_lists_dir: Path, **kwargs):
        Extension.__init__(self, name, sources=[], **kwargs)
        self.cmake_lists_dir = str(cmake_lists_dir.resolve())


class cmake_build_ext(build_ext):
    def build_extensions(self):
        # Ensure that CMake is present and working
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError("Cannot find CMake executable")

        for ext in self.extensions:

            extdir = os.path.abspath(
                os.path.dirname(self.get_ext_fullpath(ext.name))
            )

            cmake_args = [
                "-DCMAKE_BUILD_TYPE=Release",
                # Ask CMake to place the resulting library in the directory
                # containing the extension
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
                # Other intermediate static libraries are placed in a
                # temporary build directory instead
                f"-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={self.build_temp}",
            ]

            # We can handle some platform-specific settings at our discretion
            if platform.system() == "Darwin" and platform.machine() == "arm64":
                cmake_args.append("-DUSE_SSE=OFF")

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)

            # Config
            subprocess.check_call(
                ["cmake", ext.cmake_lists_dir] + cmake_args,
                cwd=self.build_temp,
            )

            # Build
            subprocess.check_call(
                ["cmake", "--build", "."], cwd=self.build_temp
            )

            binaries = glob.glob(str(Path(self.build_temp) / "reg-apps" / "*"))
            binaries = [Path(b) for b in binaries]
            binaries = [b for b in binaries if b.suffix == "" and b.is_file()]

            bin_dir = Path(extdir) / "brainreg" / "nifty_reg" / "bin"
            bin_dir.mkdir(exist_ok=True)
            for b in binaries:
                b.replace(bin_dir / b.name)


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
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
    "napari[pyside2]>=0.3.7",
    "brainglobe-napari-io",
    "brainreg-segment>=0.0.2",
]


setup(
    name="brainreg",
    version="0.3.1",
    description="Automated 3D brain registration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black",
            "pytest-cov",
            "pytest",
            "coverage",
            "bump2version",
            "pre-commit",
            "flake8",
        ]
    },
    python_requires=">=3.7",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "brainreg = brainreg.cli:main",
        ]
    },
    include_package_data=True,
    author="Adam Tyson, Charly Rousseau",
    author_email="code@adamltyson.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
    ext_modules=[
        CMakeExtension(
            "niftyreg", Path(this_directory) / "brainreg" / "nifty_reg" / "src"
        )
    ],
    cmdclass={"build_ext": cmake_build_ext},
)
