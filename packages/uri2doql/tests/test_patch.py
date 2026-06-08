from pathlib import Path

from uri2doql.patch import append_uri, patch_uri, replace_block_in_text


def test_replace_block_in_text() -> None:
    text = 'app { name: "Old"; }\nentity[name="Contact"] { first_name: string; }\n'
    updated = replace_block_in_text(
        text,
        ["entity", "Contact"],
        'entity[name="Contact"] { first_name: string; email: string; }',
    )
    assert "email: string" in updated
    assert "Old" in updated


def test_patch_and_append(tmp_path: Path) -> None:
    doc = tmp_path / "app.doql.less"
    doc.write_text(
        'app { name: "Demo"; }\nentity[name="Contact"] { first_name: string; }\n',
        encoding="utf-8",
    )
    fragment = tmp_path / "contact.less"
    fragment.write_text('entity[name="Contact"] { first_name: string; email: string; }\n', encoding="utf-8")

    patched = patch_uri(
        f"doql://block/entity/Contact?file={doc}",
        content=fragment.read_text(encoding="utf-8"),
    )
    assert patched.ok is True
    assert "email: string" in doc.read_text(encoding="utf-8")

    extra = tmp_path / "extra.less"
    extra.write_text('workflow[name="test"] { trigger: manual; }\n', encoding="utf-8")
    appended = append_uri(str(doc), content=extra.read_text(encoding="utf-8"), file=str(doc))
    assert appended.ok is True
    assert "workflow[name=\"test\"]" in doc.read_text(encoding="utf-8")
