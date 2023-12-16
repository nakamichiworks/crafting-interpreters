import textwrap

import pytest

from lox import Lox


def test_for_fibonacci(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
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
    lox = Lox()
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


@pytest.mark.freeze_time("2023-12-16 18:17:00")
def test_native_function(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        var t = clock();
        print t;
        """
    )
    expected = 1702750620
    lox.run(source)
    actual = int(capsys.readouterr().out)
    assert actual == expected


def test_lox_function(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        fun sayHi(first, last) {
            print "Hi, " + first + " " + last + "!";
        }

        sayHi("Dear", "Reader");
        """
    )
    expected = "Hi, Dear Reader!"
    lox.run(source)
    actual = capsys.readouterr().out.strip()
    assert actual == expected


def test_fibonacci_recursion(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        fun fib(n) {
            if (n <= 1) return n;
            return fib(n - 2) + fib(n - 1);
        }

        for (var i = 0; i < 10; i = i + 1) {
            print fib(i);
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
        13
        21
        34
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_counter(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        fun makeCounter() {
            var i = 0;
            fun count() {
                i = i + 1;
                print i;
            }
            return count;
        }

        var counter = makeCounter();
        counter();
        counter();
        """
    )
    expected = textwrap.dedent(
        """\
        1
        2
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_lexical_scope(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        var a = "global";
        {
            fun showA() {
                print a;
            }

            showA();
            var a = "block";
            showA();
        }
        """
    )
    expected = textwrap.dedent(
        """\
        global
        global
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_class_instantiation(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Bagel {}
        var bagel = Bagel();
        print bagel;
        """
    )
    expected = textwrap.dedent(
        """\
        Bagel instance
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_method_call(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Bacon {
            eat() {
                print "Crunch crunch crunch!";
            }
        }

        Bacon().eat();
        """
    )
    expected = textwrap.dedent(
        """\
        Crunch crunch crunch!
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_this(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Person {
            sayName() {
                print this.name;
            }
        }

        var jane = Person();
        jane.name = "Jane";

        var bill = Person();
        bill.name = "Bill";

        bill.sayName = jane.sayName;
        bill.sayName();
        """
    )
    expected = textwrap.dedent(
        """\
        Jane
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_init_1(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Foo {
            init() {
                print this;
            }
        }

        var foo = Foo();
        print foo.init();
        """
    )
    expected = textwrap.dedent(
        """\
        Foo instance
        Foo instance
        Foo instance
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_init_2(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Foo {
            init() {
                return "something else";
            }
        }
        """
    )
    expected = textwrap.dedent(
        """\
        [line 3] Error at 'return': Can't return a value from an initializer.
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_init_3(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Foo {
            init() {
                return;
            }
        }

        var foo = Foo();
        print foo.init();
        """
    )
    expected = textwrap.dedent(
        """\
        Foo instance
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_superclass(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Doughnut {
            cook() {
                print "Fry until golden brown.";
            }
        }
        class BostonCream < Doughnut {}
        BostonCream().cook();
        """
    )
    expected = textwrap.dedent(
        """\
        Fry until golden brown.
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_super_method(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Doughnut {
            cook() {
                print "Fry until golden brown.";
            }
        }
        class BostonCream < Doughnut {
            cook() {
                super.cook();
                print "Pipe full of custard and coat with chocolate.";
            }
        }
        BostonCream().cook();
        """
    )
    expected = textwrap.dedent(
        """\
        Fry until golden brown.
        Pipe full of custard and coat with chocolate.
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_invalid_super_1(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        class Eclair {
            cook() {
                super.cook();
                print "Pipe full of creme patissiere.";
            }
        }
        """
    )
    expected = textwrap.dedent(
        """\
        [line 3] Error at 'super': Can't use 'super' in a class with no superclass.
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected


def test_invalid_super_2(capsys: pytest.CaptureFixture[str]):
    lox = Lox()
    source = textwrap.dedent(
        """\
        super.method();
        """
    )
    expected = textwrap.dedent(
        """\
        [line 1] Error at 'super': Can't use 'super' outside of a class
        """
    )
    lox.run(source)
    actual = capsys.readouterr()
    assert actual.out == expected
