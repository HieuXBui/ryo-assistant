#!/usr/bin/env python3
"""
Setup script for Ryo AI Assistant
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ryo-assistant",
    version="1.0.0",
    author="Ryo AI Assistant Team",
    author_email="your-email@example.com",
    description="A sophisticated voice-activated AI assistant",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ryo-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ryo=core.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.txt", "*.md"],
    },
    keywords="ai assistant voice speech recognition text-to-speech wake-word",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ryo-assistant/issues",
        "Source": "https://github.com/yourusername/ryo-assistant",
        "Documentation": "https://github.com/yourusername/ryo-assistant#readme",
    },
) 