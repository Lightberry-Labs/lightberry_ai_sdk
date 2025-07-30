"""
Setup script for lightberry-ai package
"""

from setuptools import setup, find_packages

setup(
    name="lightberry-ai",
    use_scm_version=True,
    packages=find_packages(),
    python_requires=">=3.8",
)