"""Shared utilities for doql plugins.

This package provides common functionality used across all doql plugins
to reduce code duplication and ensure consistency.
"""
from __future__ import annotations

from .base import plugin_generate
from .readme import generate_readme

__all__ = ["plugin_generate", "generate_readme"]
