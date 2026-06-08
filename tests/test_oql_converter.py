from doql.importers.oql_converter import convert_dsl_to_doql


def test_convert_dsl_to_doql() -> None:
    dsl_text = """
    VERSION: 4
    GOAL:
      SET NAME 'Test spadku cisnienia automatu'
      LOG 'TASK Ustaw przeplyw regulator 50 l/min'
      SET pompa_1 1
      IF 'cisnienie' '0.5 .. 3.5 mbar'
        CORRECT 'cisnienie w zakresie 0.5 .. 3.5 mbar'
        ERROR 'cisnienie poza zakresem 0.5 .. 3.5 mbar'
    """
    doql = convert_dsl_to_doql(dsl_text)
    assert 'workflow[name="test_spadku_cisnienia_automatu"]' in doql
    assert 'step-1: run cmd=echo "TASK Ustaw przeplyw regulator 50 l/min";' in doql
    assert 'step-2: run cmd="pompa_1 SET 1";' in doql
    assert "assert cond=" in doql
