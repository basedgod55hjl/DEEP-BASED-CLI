#!/usr/bin/env python3
"""
BASED GOD CODER CLI Setup Script
Made by @Lucariolucario55 on Telegram
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="based-god-coder-cli",
    version="1.0.0",
    author="@Lucariolucario55",
    author_email="your-email@example.com",
    description="The ultimate AI-powered command-line interface for developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Terminals",
        "Topic :: Software Development",
        "Topic :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "based-god-cli=based_god_unified_cli:main",
            "bgc=based_god_unified_cli:main",
        ],
    },
    keywords="ai cli development coding assistant deepseek terminal",
    project_urls={
        "Bug Reports": "https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI/issues",
        "Source": "https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI",
        "Telegram": "https://t.me/Lucariolucario55",
    },
)