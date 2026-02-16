import subprocess
import sys

import sbtq


def test_version_non_empty() -> None:
    assert isinstance(sbtq.__version__, str)
    assert sbtq.__version__.strip() != ""


def test_module_runs() -> None:
    result = subprocess.run([sys.executable, "-m", "sbtq"], capture_output=True, text=True)
    assert result.returncode == 0
