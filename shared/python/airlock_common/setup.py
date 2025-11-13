"""
Setup configuration for airlock_common package
"""
from setuptools import setup

setup(
    name="airlock-common",
    version="0.1.0",
    description="Shared Python utilities and models for Airlock",
    packages=["airlock_common"],
    package_dir={"airlock_common": "."},
    install_requires=[
        "sqlalchemy>=2.0.0,<3.0.0",
        "asyncpg>=0.29.0,<1.0.0",
        "psycopg2-binary>=2.9.9,<3.0.0",
        "alembic>=1.13.0,<2.0.0",
        "typing-extensions>=4.8.0",
        "PyJWT>=2.9.0,<3.0.0",
        "cryptography>=43.0.0,<44.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.4.0,<8.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "pytest-cov>=4.1.0,<5.0.0",
            "pytest-bdd>=7.1.0,<8.0.0",
        ],
    },
    python_requires=">=3.11",
)

