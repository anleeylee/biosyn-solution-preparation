"""Tests for BioSyn Solution Preparation Batch."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from calculator import SolutionPreparator, Solution, Component


def test_molar_calculation():
    p = SolutionPreparator()
    sol = Solution(
        name="NaCl 0.1M", final_volume=500,
        components=[Component(
            name="NaCl", target_concentration=0.1,
            concentration_unit="M", molecular_weight=58.44,
        )],
    )
    result = p.prepare(sol)
    assert len(result.component_results) == 1
    assert abs(result.component_results[0].amount - 2.922) < 0.01


def test_purity_correction():
    p = SolutionPreparator()
    sol = Solution(
        name="Test", final_volume=100,
        components=[Component(
            name="R", target_concentration=1,
            concentration_unit="M", molecular_weight=100,
            purity=50.0,
        )],
    )
    result = p.prepare(sol)
    assert abs(result.component_results[0].amount - 20.0) < 0.1


def test_from_stock():
    p = SolutionPreparator()
    sol = Solution(
        name="Dilute", final_volume=100,
        components=[Component(
            name="R", target_concentration=10,
            concentration_unit="mM", stock_concentration=100,
        )],
    )
    result = p.prepare(sol)
    assert abs(result.component_results[0].amount - 10.0) < 0.1


def test_target_gt_stock():
    p = SolutionPreparator()
    sol = Solution(
        name="Bad", final_volume=100,
        components=[Component(
            name="R", target_concentration=200,
            concentration_unit="mM", stock_concentration=100,
        )],
    )
    result = p.prepare(sol)
    assert len(result.warnings) > 0


if __name__ == "__main__":
    test_molar_calculation(); test_purity_correction()
    test_from_stock(); test_target_gt_stock()
    print("All tests passed!")
