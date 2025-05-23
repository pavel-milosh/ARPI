from setuptools import setup, find_packages


setup(
    name="arpi",
    version="0.1.96",
    packages=find_packages(),
    install_requires=[
        "aiogram>=3.0",
        "tqdm",
        "blake3"
    ],
    entry_points={
        "console_scripts": [
            "arpi=arpi.__main__:main",
        ],
    },
    python_requires=">=3.10",
)