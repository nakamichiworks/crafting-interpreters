import textwrap

import pytest

import lox


def test_scope(capsys: pytest.CaptureFixture[str]):
    source = textwrap.dedent(
        """\
        var a = "global a";
        var b = "global b";
        var c = "global c";
        {
            var a = "outer a";
            var b = "outer b";
            {
                var a = "inner a";
                print a;
                print b;
                print c;
            }
            print a;
            print b;
            print c;
        }
        print a;
        print b;
        print c;
        """
    )
    expected = textwrap.dedent(
        """\
        inner a
        outer b
        global c
        outer a
        outer b
        global c
        global a
        global b
        global c
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected
