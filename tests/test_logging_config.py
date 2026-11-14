import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class LoggingConfigTest(unittest.TestCase):
    def test_configured_log_uses_application_format(self) -> None:
        script = """
import logging
from logging_config import configure_logging

configure_logging()
logging.getLogger("logging_probe").warning("formatted message")
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=PROJECT_ROOT / "src",
            env=os.environ.copy(),
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(
            result.stderr,
            re.compile(
                r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| WARNING  \| "
                r"logging_probe \d+ \| formatted message$",
                re.MULTILINE,
            ),
        )


if __name__ == "__main__":
    unittest.main()
