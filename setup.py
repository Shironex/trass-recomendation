from setuptools import setup, find_packages

setup(
    name="trass-recomendation",
    version="0.1.0",
    packages=find_packages(include=["src", "src.*"]),
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.6.1",
        "colorama>=0.4.6",
        "requests>=2.31.0",
        "pyqtgraph>=0.13.3",
        "numpy>=1.24.4",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "watchdog>=4.0.2",
        ],
        "build": [
            "pyinstaller>=6.0.0",
            "pillow>=9.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'trass-run=src.main:main',
            'trass-build-exe=src.tools.build_exe:main',
            'trass-create-icon=src.tools.create_icon:main',
        ],
    },
    python_requires=">=3.8",
) 