from pathlib import Path
import tempfile

from sbtq.robustness_sweep import run_sweep


def test_robustness_sweep_small() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        summary = run_sweep(out_dir, seeds=[0, 1])
        assert (out_dir / "results" / "robustness_summary.json").exists()
        assert summary["overall_ok"] is True
