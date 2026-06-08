"""URI → DOQL addressing, query, materialization and patch."""

from uri2doql.materialize import MaterializeResult, materialize_uri
from uri2doql.nlp2uri import best_uri, nlp2uri
from uri2doql.patch import PatchResult, apply_uri, append_uri, patch_uri, update_uri
from uri2doql.query import QueryResult, query_uri
from uri2doql.resolve import ResolvedDoqlUri, resolve_prompt_to_doql_uri
from uri2doql.uri import (
    DOQL_SCHEME,
    build_doql_uri_index,
    is_doql_uri,
    uri_for_block,
    uri_for_file,
    uri_for_generate,
)

__all__ = [
    "DOQL_SCHEME",
    "MaterializeResult",
    "PatchResult",
    "QueryResult",
    "ResolvedDoqlUri",
    "apply_uri",
    "append_uri",
    "best_uri",
    "build_doql_uri_index",
    "is_doql_uri",
    "materialize_uri",
    "nlp2uri",
    "patch_uri",
    "query_uri",
    "resolve_prompt_to_doql_uri",
    "update_uri",
    "uri_for_block",
    "uri_for_file",
    "uri_for_generate",
]
