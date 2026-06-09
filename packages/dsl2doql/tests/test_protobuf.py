from dsl2doql.codec import encode_protobuf, decode_protobuf, roundtrip_text
from dsl2doql.schema_registry import validate_schema_registry


def test_protobuf_roundtrip() -> None:
    line = "QUERY doql://block/app FORMAT json"
    assert "QUERY" in roundtrip_text(line)
    assert decode_protobuf(encode_protobuf(line)) == line


def test_schema_registry() -> None:
    assert validate_schema_registry() == []
