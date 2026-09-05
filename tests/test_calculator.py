"""
Basic unit tests for the calculator engine and the AI natural-language
parser. Run with:

    python -m unittest discover tests
"""

import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import ai_parser
from calculator_engine import CalculatorError, evaluate


class TestCalculatorEngine(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(evaluate("2 + 3"), 5)

    def test_operator_precedence(self):
        self.assertEqual(evaluate("2 + 3 * 4"), 14)

    def test_parentheses(self):
        self.assertEqual(evaluate("(2 + 3) * 4"), 20)

    def test_division_by_zero(self):
        with self.assertRaises(CalculatorError):
            evaluate("5 / 0")

    def test_sqrt_function(self):
        self.assertEqual(evaluate("sqrt(16)"), 4)

    def test_negative_numbers(self):
        self.assertEqual(evaluate("-5 + 10"), 5)

    def test_empty_expression(self):
        with self.assertRaises(CalculatorError):
            evaluate("")

    def test_blocks_unsafe_code(self):
        with self.assertRaises(CalculatorError):
            evaluate("__import__('os').system('echo hi')")


class TestAIParser(unittest.TestCase):
    def test_plus(self):
        self.assertEqual(ai_parser.parse("what is 5 plus 3"), "5 + 3")

    def test_minus(self):
        self.assertEqual(ai_parser.parse("10 minus 4"), "10 - 4")

    def test_times(self):
        self.assertEqual(ai_parser.parse("4 times 6"), "4 * 6")

    def test_divided_by(self):
        self.assertEqual(ai_parser.parse("20 divided by 5"), "20 / 5")

    def test_sqrt_phrase(self):
        self.assertEqual(ai_parser.parse("square root of 81"), "sqrt(81)")

    def test_word_numbers(self):
        self.assertEqual(ai_parser.parse("five plus three"), "5 + 3")

    def test_nonsense_raises(self):
        with self.assertRaises(ValueError):
            ai_parser.parse("hello there")


if __name__ == "__main__":
    unittest.main()
