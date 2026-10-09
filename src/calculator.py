"""
Solution preparation calculation engine.

Supports: molar solutions, stock dilutions, mass concentration, percentage (w/v, v/v, w/w).
All calculations include audit trail: input → unit normalization → formula → substitution → result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Unit conversions to base SI units
# Mass: grams, Volume: liters, Molar: mol/L
MASS_TO_G = {"g": 1.0, "mg": 1e-3, "µg": 1e-6, "ng": 1e-9}
VOL_TO_L = {"L": 1.0, "mL": 1e-3, "µL": 1e-6}
MOLAR_TO_MOLAR = {"M": 1.0, "mM": 1e-3, "µM": 1e-6, "nM": 1e-9}
MASS_CONC_TO_G_PER_L = {"g/L": 1.0, "mg/mL": 1.0, "µg/mL": 1e-3}


@dataclass
class Component:
    """A single component in a solution preparation."""
    name: str
    target_concentration: float
    concentration_unit: str
    molecular_weight: float = 0.0       # g/mol (for molar)
    stock_concentration: float = 0.0    # for "from stock" mode
    stock_unit: str = ""
    purity: float = 100.0               # %, e.g. 98.0
    density: float = 1.0                # g/mL (for v/v liquids)
    notes: str = ""


@dataclass
class Solution:
    """A solution to prepare."""
    name: str
    final_volume: float                 # mL
    volume_unit: str = "mL"
    components: List[Component] = field(default_factory=list)
    batch: str = "Default"
    notes: str = ""


@dataclass
class ComponentResult:
    """Calculation result for one component."""
    component_name: str
    mode: str                           # molar | from_stock | mass_conc | percentage
    amount: float                       # mass in grams OR volume in mL
    amount_unit: str
    audit_trail: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class SolutionResult:
    """Full result for one solution."""
    solution_name: str
    batch: str
    final_volume_ml: float
    component_results: List[ComponentResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class SolutionPreparator:
    """Compute solution preparation calculations."""

    def prepare(self, solution: Solution) -> SolutionResult:
        """
        Compute preparation amounts for all components in a solution.

        Args:
            solution: Solution definition with components.

        Returns:
            SolutionResult with calculated amounts and audit trails.
        """
        result = SolutionResult(
            solution_name=solution.name,
            batch=solution.batch,
            final_volume_ml=solution.final_volume,
        )

        for comp in solution.components:
            try:
                cr = self._calc_component(comp, solution.final_volume)
                result.component_results.append(cr)
                result.warnings.extend(cr.warnings)
            except Exception as exc:
                result.component_results.append(ComponentResult(
                    component_name=comp.name,
                    mode="ERROR",
                    amount=0, amount_unit="",
                    audit_trail=f"ERROR: {exc}",
                    warnings=[str(exc)],
                ))
                result.warnings.append(f"{comp.name}: {exc}")

        return result

    def _calc_component(self, comp: Component, final_volume_ml: float) -> ComponentResult:
        """Calculate amount needed for a single component."""

        # Determine mode
        if comp.molecular_weight > 0 and comp.stock_concentration == 0:
            return self._calc_molar(comp, final_volume_ml)
        elif comp.stock_concentration > 0:
            return self._calc_from_stock(comp, final_volume_ml)
        elif comp.concentration_unit in MASS_CONC_TO_G_PER_L:
            return self._calc_mass_conc(comp, final_volume_ml)
        elif "%" in comp.concentration_unit:
            return self._calc_percentage(comp, final_volume_ml)
        else:
            return self._calc_molar(comp, final_volume_ml)

    def _calc_molar(self, comp: Component, final_vol_ml: float) -> ComponentResult:
        """Molar solution: mass = C × V × MW."""
        c_molar = comp.target_concentration * MOLAR_TO_MOLAR.get(comp.concentration_unit, 1.0)
        v_l = final_vol_ml / 1000.0
        mass_g = c_molar * v_l * comp.molecular_weight

        # Purity correction
        purity_fraction = comp.purity / 100.0
        if purity_fraction <= 0:
            raise ValueError(f"Purity must be > 0%, got {comp.purity}%")
        corrected_mass = mass_g / purity_fraction

        audit = (
            f"mass = C × V × MW\n"
            f"     = {c_molar:.6f} mol/L × {v_l:.4f} L × {comp.molecular_weight:.2f} g/mol\n"
            f"     = {mass_g:.4f} g"
        )
        if comp.purity < 100.0:
            audit += f"\npurity correction: {mass_g:.4f} / {purity_fraction} = {corrected_mass:.4f} g"

        warnings = []
        if comp.purity > 100:
            warnings.append(f"Purity {comp.purity}% > 100% — check input")
        if corrected_mass > 100:
            warnings.append(f"Mass {corrected_mass:.2f} g is large — verify")

        return ComponentResult(
            component_name=comp.name,
            mode="molar",
            amount=round(corrected_mass, 4),
            amount_unit="g",
            audit_trail=audit,
            warnings=warnings,
        )

    def _calc_from_stock(self, comp: Component, final_vol_ml: float) -> ComponentResult:
        """Dilute from stock: C1V1 = C2V2."""
        c1 = comp.stock_concentration
        c2 = comp.target_concentration
        v2 = final_vol_ml

        if c2 > c1:
            raise ValueError(
                f"Target concentration {c2} > stock concentration {c1}. "
                f"Cannot dilute to a higher concentration."
            )

        v1 = (c2 * v2) / c1 if c1 > 0 else 0
        diluent = v2 - v1

        audit = (
            f"V1 = C2 × V2 / C1\n"
            f"   = {c2} × {v2} / {c1}\n"
            f"   = {v1:.2f} mL stock + {diluent:.2f} mL diluent"
        )

        warnings = []
        if v1 < 0.05:
            warnings.append(f"Stock volume {v1:.3f} mL < 50 µL — pipetting accuracy concern")

        return ComponentResult(
            component_name=comp.name,
            mode="from_stock",
            amount=round(v1, 4),
            amount_unit="mL (stock)",
            audit_trail=audit,
            warnings=warnings,
        )

    def _calc_mass_conc(self, comp: Component, final_vol_ml: float) -> ComponentResult:
        """Mass concentration: e.g. mg/mL → g/L."""
        c_g_per_l = comp.target_concentration * MASS_CONC_TO_G_PER_L.get(comp.concentration_unit, 1.0)
        v_l = final_vol_ml / 1000.0
        mass_g = c_g_per_l * v_l
        purity_fraction = comp.purity / 100.0
        corrected_mass = mass_g / purity_fraction if purity_fraction > 0 else mass_g

        audit = (
            f"mass = C × V\n"
            f"     = {c_g_per_l:.4f} g/L × {v_l:.4f} L\n"
            f"     = {mass_g:.4f} g"
        )

        return ComponentResult(
            component_name=comp.name,
            mode="mass_conc",
            amount=round(corrected_mass, 4),
            amount_unit="g",
            audit_trail=audit,
        )

    def _calc_percentage(self, comp: Component, final_vol_ml: float) -> ComponentResult:
        """Percentage concentration (w/v, v/v, w/w)."""
        pct_str = comp.concentration_unit.lower()
        pct_value = comp.target_concentration

        if "w/v" in pct_str:
            # g per 100 mL
            mass_g = pct_value / 100.0 * final_vol_ml
            audit = f"{pct_value}% w/v = {pct_value} g / 100 mL × {final_vol_ml} mL = {mass_g:.4f} g"
            return ComponentResult(comp.name, "percentage_w/v", round(mass_g, 4), "g", audit)

        elif "v/v" in pct_str:
            volume_ml = pct_value / 100.0 * final_vol_ml
            audit = f"{pct_value}% v/v = {pct_value} mL / 100 mL × {final_vol_ml} mL = {volume_ml:.4f} mL"
            return ComponentResult(comp.name, "percentage_v/v", round(volume_ml, 4), "mL", audit)

        elif "w/w" in pct_str:
            # Requires density
            if comp.density <= 0:
                raise ValueError("w/w percentage requires density input")
            total_mass_g = final_vol_ml * comp.density
            mass_g = pct_value / 100.0 * total_mass_g
            audit = f"{pct_value}% w/w → {mass_g:.4f} g (requires density={comp.density} g/mL)"
            return ComponentResult(comp.name, "percentage_w/w", round(mass_g, 4), "g", audit)

        else:
            raise ValueError(f"Unknown percentage unit: {comp.concentration_unit}")
