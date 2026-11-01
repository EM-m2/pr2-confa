import unittest
from unittest.mock import patch

from src.main import parse_args


class ConfigTests(unittest.TestCase):
    """Проверки параметров командной строки."""

    def test_valid_config(self):
        """Проверяет корректные параметры."""
        arguments = [
            "program",
            "--package", "A",
            "--source", "fixtures/chain.json",
            "--test",
            "--version", "1.0.0",
            "--depth", "3",
        ]

        with patch("sys.argv", arguments):
            args = parse_args()

        self.assertEqual(args.package, "A")
        self.assertEqual(args.depth, 3)
        self.assertTrue(args.test)

    def test_negative_depth(self):
        """Проверяет ошибку отрицательной глубины."""
        arguments = [
            "program",
            "--package", "A",
            "--source", "fixtures/chain.json",
            "--test",
            "--version", "1.0.0",
            "--depth", "-1",
        ]

        with patch("sys.argv", arguments):
            with self.assertRaises(SystemExit):
                parse_args()


if __name__ == "__main__":
    unittest.main()
