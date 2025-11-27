"""
Setup script for Essay Evaluator package.
"""
try:
    from setuptools import setup, find_packages
except ImportError:
    raise ImportError(
        "setuptools is required to install this package. "
        "Install it with: pip install setuptools"
    )

from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README_NEW.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="essay-evaluator",
    version="1.0.0",
    author="Vania Janet",
    author_email="vania@example.com",
    description="AI-Powered Academic Essay Assessment System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vania-Janet/llm-essay-reviewer",
    packages=find_packages(exclude=["tests", "docs", "scripts"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "essay-evaluator=essay_evaluator.api.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "essay_evaluator": [
            "web/static/**/*",
            "web/templates/**/*",
        ],
    },
    zip_safe=False,
)
