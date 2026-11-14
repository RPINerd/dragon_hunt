import os
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_configured_log_uses_application_format() -> None:
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

    assert result.returncode == 0, result.stdout + result.stderr
    assert re.search(
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| WARNING  \| "
        r"logging_probe \d+ \| formatted message$",
        result.stderr,
        re.MULTILINE,
    )
