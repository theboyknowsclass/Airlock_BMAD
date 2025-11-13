"""
Alembic environment configuration
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context

# Add the parent directory to the path so we can import airlock_common
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import database models
from airlock_common.db.base import Base
from airlock_common.db.models import (
    User,
    PackageSubmission,
    PackageRequest,
    Package,
    Workflow,
    CheckResult,
    AuditLog,
    APIKey,
    PackageUsage,
    LicenseAllowlist,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from environment variables (sync version for Alembic)"""
    # Try to load from .env.dev file if it exists (for development)
    env_file_path = os.path.join(
        os.path.dirname(__file__), 
        "../../../../.env.dev"
    )
    if os.path.exists(env_file_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file_path, override=False)  # Don't override existing env vars
        except ImportError:
            # If python-dotenv not installed, manually parse .env.dev
            try:
                with open(env_file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key.startswith('POSTGRES_') and key not in os.environ:
                                os.environ[key] = value
            except Exception:
                pass  # If parsing fails, use defaults
    
    # Convert asyncpg URL to psycopg2 URL for Alembic (which uses sync SQLAlchemy)
    # Defaults match .env.dev values
    # Note: When running from host machine, use "localhost" not "postgres" (Docker service name)
    host = os.getenv("POSTGRES_HOST", "localhost")
    # If host is "postgres" (Docker service name), change to "localhost" for host machine access
    if host == "postgres":
        host = "localhost"
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "airlock_dev")
    user = os.getenv("POSTGRES_USER", "airlock_dev")
    password = os.getenv("POSTGRES_PASSWORD", "dev_password_change_me")
    
    # Use psycopg2 for Alembic (synchronous)
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Override the sqlalchemy.url from alembic.ini with environment variable
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

