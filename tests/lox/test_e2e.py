import textwrap

import pytest

import lox


def test_for_fibonacci(capsys: pytest.CaptureFixture[str]):
    source = textwrap.dedent(
        """\
        var a = 0;
        var temp;
        for (var b = 1; a < 10; b = temp + b) {
            print a;
            temp = a;
            a = b;
        }
        """
    )
    expected = textwrap.dedent(
        """\
        0
        1
        1
        2
        3
        5
        8
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


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
