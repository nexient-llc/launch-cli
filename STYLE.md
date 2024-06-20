# Code Style

This document captures our style guidelines for code in this repository. This is a living document and is subject to change. Additionally, there are places within the codebase that do not conform 100% to this document, and will need to be addressed.

## PEP 8

Unless otherwise noted, this repository follows [PEP 8 guidelines](https://peps.python.org/pep-0008/#package-and-module-names) with regard to code format and standards. We use [black](https://github.com/psf/black) and [isort](https://pycqa.github.io/isort/) to automatically format code on commit. Ensure that you `make configure` upon cloning the repository to set up our pre-commit hooks. If you submit code that hasn't been run through the formatters, you will be asked to fix this prior to any changes being merged.

In addition to PEP 8, we strongly suggest reviewing the following PEPs, as they will be enforced going forward:

- [PEP 257](https://peps.python.org/pep-0257/) - Docstrings

    For top-level Click functions, one-liner docstrings are preferred, since Click utilizes these docstrings to populate its helptext and self documenting command line functions.

    Everywhere else, we utilize multiline docstrings using the the Google convention (typed). VSCode users may choose to install the [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) extension to assist with docstring creation.

    Multiline module docstrings are optional but encouraged.

- [PEP 484](https://peps.python.org/pep-0484/) - Function Annotations

    All function arguments and return types should be annotated.

- [PEP 526](https://peps.python.org/pep-0526/) - Variable Annotations

    If it's not immediately clear from the variable's assignment what type it should be, it should have an annotation.

    ```py
    # These are fine, their type is explicit from assignment:
    foo = 1
    bar = "hello world"

    # This is ambiguous and should be avoided:
    baz = {}

    # Instead, annotate the declaration to include the expected types:
    baz: dict[str, int] = {}
    ```

Prefer simple types, but when complex types are required, you are encouraged to define them as a standalone type at the top of the module and then use them throughout in function and variable annotations.

```py
# Readability suffers as the number of arguments and their complexity grows:
def handle_bar(bar: dict[str, set[str]]) -> dict[str, set[str]]:
    output: dict[str, set[str]] = {}
    ...

# Do this instead:
MyComplexType = dict[str, set[str]]

def handle_bar(bar: MyComplexType) -> MyComplexType:
    output: MyComplexType = {}
    ...

# This further promotes reusability through importing existing types:
from your_module import MyComplexType
```

## Click Specifics

We utilize the `Click` library to build our command line interface.

### Outputs

Never `print()`, use `click.echo()` and `click.secho()` from a top-level command if you need to write text directly to the terminal.

When using `click.secho()`, the following styles are recommended:

```py
click.secho("Denotes a failure, text will appear red on most terminals", fg="red")
click.secho("Denotes a warning, yellow on most terminals", fg="yellow")
```

### Command-Line Options

Prefer options over arguments. Click's `Option` type is [more flexible](https://click.palletsprojects.com/en/8.1.x/parameters/#differences) and is preferred to the `Argument` type. If you have a required value that does not have a reasonable default, ensure you use the `required` parameter. Rather than utilizing variadic arguments, use the `multiple` arg on your `Option`.

When defining options on a given command, at a minimum you should specify the [type](https://click.palletsprojects.com/en/8.1.x/parameters/#parameter-types) and a help string that describes the option. Options must always include a long-form flag (e.g. `--verbose`) and preferably include a short-form flag (e.g. `-v`) when possible.

When handling boolean options, use `is_flag` to detect presence or lack of an option, rather than asking the user for a truthy or falsy value.

More details on the Parameters API is [available here](https://click.palletsprojects.com/en/8.1.x/api/#parameters).

## `pathlib` over `os`

Prefer `pathlib` over the `os` module, as it's more agnostic to different operating systems and file systems. There are exceptions to this rule (Windows file permissions are poorly-supported in either) but in general, if you're interacting with the filesystem (including reading from and writing to files), you should be using `pathlib`.

When using `pathlib`, prefer the functional style over the operator-overloading style, that is:

```py
# Prefer this
Path(“.”).joinpath(f“{subdir}/{bottom_level}/baz.txt”)
# or this
Path(“.”).joinpath(subdir).joinpath(bottom_level).joinpath(“baz.txt”)

# Avoid this:
Path(“.”) / subdir / bottom_level / “baz.txt”
```

## Comprehensions and Looping

Prefer comprehensions for simple cases; they're almost always more performant and easier to read.

```py
# Avoid this:
simple_list = []
for foo in foos:
    simple_list.append(foo.bar)

# Avoid this:
simple_dict = {}
for thing in things:
    if thing.property:
        simple_dict[thing] = transform(thing)

# Instead, prefer a comprehension
simple_list = [foo.bar for foo in foos]
simple_dict = {thing: transform(thing) for thing in things if thing.property}
```

Comprehensions can become complex quickly, especially when using filtering criteria. Avoid the use of comprehensions for nested expressions. Use your best judgement to determine when you have too many filter criteria. Additionally, avoid using comprehensions to iterate over a returnless function.

```py
# Avoid complex and nested comprehensions, looping is easier for most people to follow
complex_result = [
    [
        expression
        for item in items
        if item.some_property == 42
    ]
    for item in items
    if item.property
    and item.another_property in another_list
]

# Avoid returnless comprehensions, even if discarding the result explicitly
_ = [do_something(bar) for bar in bars]
```

## Exception Handling

Handle exceptions with a precise exception type where possible.

```py
# Avoid overly-broad exceptions:
try:
    might_divide_by_zero(numerator, denominator)
except Exception:
    # Broad exception type, swallows inner exceptions indiscriminately

# Prefer:
try:
    might_divide_by_zero(numerator, denominator)
except ZeroDivisionError:
    # Specific type means we don't catch unexpected exceptions here
    # and they can be handled at different levels
```

Never use a bare except, as it can lead to unexpected behavior!

```py
try:
    long_running_and_might_fail()
except:
    # Now you've caught KeyboardInterrupt and can't stop your program.
```

## Logging

We utilize the stdlib `logging` module to write outputs to stdout and stderr from `launch-cli`. Do not use `print()`.

If you need to echo something without invoking `logging`, do it from the top level (in a Click command) and use either `click.echo()` or `click.secho()` if you desire styled text.

If you need to emit text from inside a library module, use `logging` with the appropriate level.

```py
# my_module.py
logger = logging.getLogger(__name__)

def my_function() -> None:
    logger.debug("Message that wouldn't normally appear")
    logger.info("Important information, should always appear")
    logger.warning("Something that may be a problem")
    logger.error("A failure, not necessarily terminal, may be able to be recovered")
    logger.critical("A failure from which we cannot recover")
```

Debug-level logs are enabled by providing the `--verbose` or `-v` flag to the `launch` command.

When logging a message inside an exception handler, use `logging.exception` which will log to the `error` level and include traceback information:

```py
try:
    might_fail()
except RuntimeError:
    logging.exception("might_fail did fail!")

# This yields a log line like:
# 2024-02-12 12:53:52 CST root    ERROR   might_fail did fail!
# Traceback (most recent call last):
#   File "...", line 2, in ...
# ZeroDivisionError: division by zero
```

## String handling

Prefer f-strings to string concatenation.

```py
# Avoid this:
results = "Your score was " + user_score + " out of " + max_score + "."

# Prefer this:
results = f"Your score was {user_score} out of {max_score}."
```

Most of the time, objects in the stdlib will provide a `__format__` magic method for use with f-strings that obviates the need for an explicit string cast. Objects that we create should define a `__repr__`, `__str__`, or `__format__` method, though this may not be necessary when using Dataclasses. Avoid explicitly casting to string inside of an f-string unless you're sure that you need to:

```py
# Avoid this:
message = f"The value is {str(some_object)}"

# Prefer this:
message = f"The value is {some_object}"
```

Building small strings iteratively is generally fine, though as the number of strings to iterate increases, Python can consume a significant amount of RAM if there are many strings, as strings containing only letters, digits, and underscores are interned by default. Prefer using `.join()`, followed by `StringIO` and finally raw concatenation.

```py
# Slowest, expensive, but fairly readable:
for word in dictionary:
    sentence += word + " "

# Better in terms of speed and RAM for larger iterables, not as readable
from io import StringIO

sentence = StringIO()
for word in dictionary:
    sentence.write(word)
sentence.getvalue()

# Best in terms of performance and readability
sentence = " ".join(dictionary)
```

For small scales (64 strings), the differences between raw concatenation and StringIO are negligible, while `.join()` is roughly 5x as fast. For a medium-scale test (64k strings), StringIO is roughly twice as fast as raw concatenation, and `.join()` is an order of magnitude faster than StringIO. For large scales (64m strings), The performance difference between raw concatenation and StringIO holds and `.join()` is two orders of magnitude faster than the others.

## Testing

Code should be covered at a minimum by unit tests, and ideally with integration tests that exercise the functionality without using mocks.

### `pytest` and `unittest`

We use `pytest` for its excellent interfaces and capabilities, you should not import and use `unittest` interfaces without a really good reason.

When mocking objects, prefer the `pytest`-style mocks over `unittest`-style decorated or context manager mocks for three reasons:

1. Decorators are zero-reuse, they must be copy-pasted around
2. Large numbers of decorators create visual clutter that makes code more difficult to read
3. `pytest` eschews context manager mocks because it provides cleanup guarantees (and reduces indent depth as a bonus!)

```py
# Avoid:
@patch(“thing.to.mock”)
@patch(“another.thing.to.mock”)
@patch(“more.things.to.mock”)
def test_my_thing():
    ...

# Avoid:
def test_my_thing():
    with patch("thing.to.mock"):
        ...

# Prefer:
def test_my_thing(mocker):
    mocker.patch(“thing.to.mock”)
    mocker.patch(“another.thing.to.mock”)
    mocker.patch(“more.things.to.mock”)
    ...

# Better yet:
def test_my_thing(my_fixture, mocker):
    # Common mocks are performed in the fixture
    mocker.patch("thing.specific.to.this.test", side_effect=ValueError)
    ...
```

If you need to reuse a series of mocks with a consistent set of side effects, create a fixture and utilize that fixture in your test code. If your side effect requirements are unique to the test function, the side effect statements belong inside the function as it's part of the test code.

When writing tests, reserve the use of decorators for test control flow, like `parametrize`, `skip`, `skipif`, `xfail`, etc.

```py
@pytest.mark.parametrize("input_a", [1,2,3])
@pytest.mark.parametrize("input_b", [4,5,6])
@pytest.mark.skipif(sys.platform.startswith("win"), reason="Doesn't work under Windows")
def test_my_thing(input_a: int, input_b: int):
    ...
```

Use of parametrization as demonstrated above is highly recommended for writing tests that test a wide range of scenarios. Consider the following example:

```py
# Avoid:
def test_scenario_one():
    assert result("one") == 1

def test_scenario_two():
    assert result("two") == 2

# Prefer:
@pytest.mark.parametrize("scenario, outcome", [
    ("one", 1),
    ("two", 2) # test cases can be added without writing additional test functions!
])
def test_scenario(scenario: str, outcome: int):
    assert result(scenario) == outcome
```

### Fixtures

Test fixtures may be added to the `conftest.py` files located under the `tests/` directory if they are intended to be shared among multiple tests within a given type (unit, integration) of test. If the fixture is specific to testing a single module, it belongs in the same file as the tests for that module.

`pytest` provides guarantees about mocking and test cleanup, but if you have the need to perform some additonal cleanup steps when using a fixture, ensure that you `yield` in the fixture and place your cleanup code after the `yield` statement:

```py
@pytest.fixture
def my_fixture(other_fixture, mocker):
    # Some setup
    yield
    # Some cleanup
```

### Test Functions vs. Test Classes

While it's perfectly acceptable to have a set of test functions at the top level of a module, use of test classes is recommended as the number of tests increase to provide a logical grouping of tests for ease of use.

```py
# Acceptable:
def test_thing_one_way():
    ...

def test_thing_another_way():
    ...

# Better:
class TestThing:
    def test_one_way():
        ...

    def test_another_way():
        ...
```

This provides a clear grouping of related code and gives you the ability to specify this grouping when running `pytest` from the command line with an explicit class name:

```sh
pytest tests/unit/my_test_file.py::TestThing
```
