"""
Setup configuration for airlock_common package
"""
from setuptools import setup, find_packages

setup(
    name="airlock-common",
    version="0.1.0",
    description="Shared Python utilities and models for Airlock",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0.0,<3.0.0",
        "asyncpg>=0.29.0,<1.0.0",
        "psycopg2-binary>=2.9.9,<3.0.0",
        "alembic>=1.13.0,<2.0.0",
        "typing-extensions>=4.8.0",
    ],
    python_requires=">=3.11",
)

