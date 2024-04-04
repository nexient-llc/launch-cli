from io import StringIO
from time import perf_counter_ns

d: list[str] = [
    "Most",
    "of",
    "the",
    "time,",
    "objects",
    "in",
    "the",
    "stdlib",
    "will",
    "provide",
    "a",
    "`__format__`",
    "magic",
    "method",
    "for",
    "use",
    "with",
    "f-strings",
    "that",
    "obviates",
    "the",
    "need",
    "for",
    "an",
    "explicit",
    "string",
    "cast.",
    "Objects",
    "that",
    "we",
    "create",
    "should",
    "define",
    "a",
    "`__repr__`,",
    "`__str__`,",
    "or",
    "`__format__`",
    "method,",
    "though",
    "this",
    "may",
    "not",
    "be",
    "necessary",
    "when",
    "using",
    "Dataclasses.",
    "Avoid",
    "explicitly",
    "casting",
    "to",
    "string",
    "inside",
    "of",
    "an",
    "f-string",
    "unless",
    "you're",
    "sure",
    "that",
    "you",
    "need",
    "to:",
]
dictionary: list[str] = []

for _ in range(1000000):
    dictionary.extend(d)


def test_naive(words: list[str]) -> int:
    start_time = perf_counter_ns()
    sentence = ""
    for word in words:
        sentence += word + " "
    end_time = perf_counter_ns()
    return end_time - start_time


def test_stringio(words: list[str]) -> int:
    start_time = perf_counter_ns()
    sentence = StringIO()
    space = " "
    for word in words:
        sentence.write(word)
        sentence.write(space)
    sentence.getvalue()
    end_time = perf_counter_ns()
    return end_time - start_time


def test_join(words: list[str]) -> int:
    start_time = perf_counter_ns()
    sentence = " ".join(words)
    end_time = perf_counter_ns()
    return end_time - start_time


print(
    f"""
{len(dictionary)=}
{test_naive(dictionary)=}
{test_stringio(dictionary)=}
{test_join(dictionary)=}
"""
)

# test_naive(dictionary)     =4169625
# test_stringio(dictionary)  =2132625
# test_join(dictionary)       =572291

# test_naive(dictionary)=   4630244875
# test_stringio(dictionary)=2206208500
# test_join(dictionary)=      60365704
