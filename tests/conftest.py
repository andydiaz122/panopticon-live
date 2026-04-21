"""Global test fixtures."""

from __future__ import annotations

import random

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def _deterministic_seeds() -> None:
    """Force deterministic random seeds across every test."""
    random.seed(42)
    np.random.seed(42)
