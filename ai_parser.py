"""
ai_parser.py
-------------
This is the "AI" layer of the app: a lightweight Natural Language
Processing (NLP) module that turns a plain-English question like

    "what is the square root of 81 plus 4"

into a math expression the calculator engine can evaluate:

    "sqrt(81) + 4"

It's built with rule-based NLP (regular expressions + a word list) rather
than a large language model. That keeps the app fast, free, and fully
self-contained -- no API keys or internet connection needed to run it.
Rule-based parsing like this is a common first step in NLP before moving
on to statistical or transformer-based intent classifiers.
"""

import re

NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20",
}

# Ordered (pattern, symbol) pairs. Longer / more specific phrases must be
# checked before shorter ones, otherwise "divided by" could get mangled by
# a rule meant for something else.
OPERATION_PATTERNS = [
    (r"\bplus\b|\badded to\b|\bsum of\b", "+"),
    (r"\bminus\b|\bsubtracted from\b|\bless\b", "-"),
    (r"\bmultiplied by\b|\bmultiplied with\b|\btimes\b", "*"),
    (r"\bdivided by\b|\bover\b", "/"),
    (r"\bmodulo\b|\bmod\b|\bremainder of\b", "%"),
    (r"\bto the power of\b|\braised to\b", "**"),
]

# Filler words are stripped LAST, after operation phrases are matched --
# some operation phrases (like "to the power of") contain words such as
# "the" that would otherwise be stripped too early and break the match.
FILLER_PATTERN = r"\bwhat('| i)?s\b|\bwhat is\b|\bcalculate\b|\bcompute\b|\bfind\b|\bplease\b|\bthe\b|\ban?\b|\?"

SQRT_PATTERN = re.compile(r"(?:square root of|sqrt of)\s*([\d.]+)")


def _words_to_numbers(text: str) -> str:
    for word, digit in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", digit, text)
    return text


def parse(text: str) -> str:
    """Convert a natural-language math question into a math expression string.

    Raises ValueError if nothing recognizable is left after parsing.
    """
    text = (text or "").lower().strip()
    text = _words_to_numbers(text)

    # Handle "square root of X" / "sqrt of X" -> sqrt(X) first, since it
    # needs to become a function call rather than a plain symbol swap.
    text = SQRT_PATTERN.sub(lambda m: f"sqrt({m.group(1)})", text)

    for pattern, symbol in OPERATION_PATTERNS:
        text = re.sub(pattern, f" {symbol} ", text)

    # Now it's safe to drop filler words like "what is" and "the".
    text = re.sub(FILLER_PATTERN, "", text)

    # Drop anything left that isn't a number, operator, parenthesis or the
    # letters needed for function names like sqrt(...).
    text = re.sub(r"[^0-9a-z+\-*/().% ]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text or not re.search(r"\d", text):
        raise ValueError("Couldn't understand that as a math question")
    return text
