from setuptools import setup

setup(
    name="pyhttp",
    version="0.1.1",
    packages=["pyhttp"],
    install_requires=[],
    entry_points={
        "console_scripts": ["pyhttp = pyhttp.cli:parse_args"],
    },
)
