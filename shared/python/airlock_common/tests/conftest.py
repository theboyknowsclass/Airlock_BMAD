"""
Pytest configuration for airlock_common tests
"""
import pytest
from pathlib import Path
from pytest_bdd import scenarios

# Discover all feature files
feature_dir = Path(__file__).parent / "features"
if feature_dir.exists():
    scenarios(str(feature_dir / "*.feature"))

