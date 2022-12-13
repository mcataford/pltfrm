import setuptools
import pathlib

PACKAGE_ROOT = pathlib.Path(__file__).parent.resolve()

version_file = pathlib.Path(PACKAGE_ROOT).joinpath("version.txt")

VERSION_STRING = (
    version_file.open(encoding="utf8").read() if version_file.exists() else "0.0.0"
)

DEV_REQUIREMENTS = ["black", "pylint", "pytest", "pytest-cov", "pyyaml"]

setuptools.setup(
    name="pltfrm",
    version=VERSION_STRING,
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[],
    extras_require={"dev": DEV_REQUIREMENTS},
    entry_points={"console_scripts": ["pltfrm=src.main:main"]},
)
