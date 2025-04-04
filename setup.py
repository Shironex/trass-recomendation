from setuptools import setup, find_packages

setup(
    name="trass-recomendation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.1",
        "colorama>=0.4.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    python_requires=">=3.8",
) 