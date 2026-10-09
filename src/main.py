"""
CLI entry point for BioSyn Solution Preparation Batch.

Usage:
    python -m src.main recipes.xlsx --output preparation_sheet.xlsx
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict

from .calculator import SolutionPreparator, Solution, Component, SolutionResult
from .exporter import export_solutions

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def read_recipes_csv(path: Path) -> List[Solution]:
    """Read batch recipe CSV file."""
    solutions: Dict[str, Solution] = {}

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sname = row.get("Solution_Name", row.get("Solution", row.get("Name", ""))).strip()
            if not sname:
                continue

            if sname not in solutions:
                solutions[sname] = Solution(
                    name=sname,
                    final_volume=float(row.get("Final_Volume", row.get("Volume", 500))),
                    batch=row.get("Batch", row.get("Group", "Default")),
                    notes=row.get("Notes", ""),
                )

            comp = Component(
                name=row.get("Component", row.get("Reagent", "")),
                target_concentration=float(row.get("Target_Concentration",
                                     row.get("Concentration", 0)) or 0),
                concentration_unit=row.get("Concentration_Unit",
                                           row.get("Unit", "mM")),
                molecular_weight=float(row.get("Molecular_Weight",
                                     row.get("MW", 0)) or 0),
                stock_concentration=float(row.get("Stock_Concentration",
                                         row.get("Stock_C", 0)) or 0),
                stock_unit=row.get("Stock_Unit", ""),
                purity=float(row.get("Purity", 100) or 100),
                density=float(row.get("Density", 1.0) or 1.0),
                notes=row.get("Component_Notes", ""),
            )
            solutions[sname].components.append(comp)

    return list(solutions.values())


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="biosyn-solution-prep",
        description="BioSyn Solution Preparation Batch — batch buffer/reagent calculator.",
        epilog="Built by BioSyn Inc. — https://biosyn-inc.com/",
    )
    parser.add_argument("input", type=Path, help="Recipe CSV / XLSX file")
    parser.add_argument("--output", "-o", type=Path,
                        default=Path("preparation_sheet.xlsx"))
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    setup_logging(args.verbose)

    try:
        solutions = read_recipes_csv(args.input)
        if not solutions:
            raise ValueError("No solutions found in input file.")

        preparator = SolutionPreparator()
        results: List[SolutionResult] = []
        for sol in solutions:
            result = preparator.prepare(sol)
            results.append(result)
            logger.info("Computed: %s (%d components)", sol.name, len(sol.components))

        export_solutions(results, args.output)

        print(f"\nPrepared {len(results)} solution(s):")
        for r in results:
            print(f"  {r.solution_name} ({r.batch}, {r.final_volume_ml} mL):")
            for cr in r.component_results:
                print(f"    {cr.component_name}: {cr.amount} {cr.amount_unit}")
            if r.warnings:
                for w in r.warnings:
                    print(f"    ⚠ {w}")
        print(f"\nResults saved to: {args.output.resolve()}")
        print("\n⚠ Verify preparation calculations against your lab SOP before use.")
        return 0
    except Exception as exc:
        logger.error("Fatal error: %s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
