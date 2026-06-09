"""DOQL control DSL — query, patch, validate and adopt manifests."""

from dsl2doql.bus import dispatch
from dsl2doql.engine import DslResult, execute_dsl, execute_dsl_line
from dsl2doql.converter import convert_dsl_to_doql

__all__ = ["DslResult", "execute_dsl", "execute_dsl_line", "convert_dsl_to_doql", "dispatch"]
