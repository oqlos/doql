"""Uncertainty module generator for ISO/IEC 17025:2017 compliance."""
from __future__ import annotations

import textwrap


def generate() -> str:
    """Generate uncertainty.py module content."""
    return textwrap.dedent('''\
        """Uncertainty budget — per JCGM 100:2008 (GUM — Guide to Expression of Uncertainty).

        Combined standard uncertainty u_c computed via root-sum-of-squares of components:
          u_c² = Σ (cᵢ · uᵢ)²

        Expanded uncertainty U = k · u_c (typically k=2 for ~95% coverage).
        """
        from __future__ import annotations

        from dataclasses import dataclass, field
        from enum import Enum
        from math import sqrt


        class UncertaintyType(str, Enum):
            TYPE_A = "A"   # Statistical (from repeated measurements)
            TYPE_B = "B"   # Non-statistical (datasheet, calibration cert, judgment)


        class Distribution(str, Enum):
            NORMAL = "normal"            # divisor = k (commonly 2)
            RECTANGULAR = "rectangular"  # divisor = √3
            TRIANGULAR = "triangular"    # divisor = √6
            U_SHAPED = "u_shaped"        # divisor = √2


        _DIVISORS = {
            Distribution.NORMAL: 1.0,   # user supplies k via coverage_factor field
            Distribution.RECTANGULAR: sqrt(3),
            Distribution.TRIANGULAR: sqrt(6),
            Distribution.U_SHAPED: sqrt(2),
        }


        @dataclass
        class UncertaintyComponent:
            """Single contribution to the uncertainty budget."""
            name: str
            value: float                              # half-width of the interval (type B) or std dev (type A)
            type: UncertaintyType = UncertaintyType.TYPE_B
            distribution: Distribution = Distribution.RECTANGULAR
            coverage_factor: float = 1.0              # k for type B with normal distribution (datasheet U)
            sensitivity: float = 1.0                  # ∂y/∂xᵢ
            unit: str = ""
            source: str = ""

            @property
            def standard_uncertainty(self) -> float:
                """u(xᵢ) — the standard uncertainty for this component."""
                if self.type == UncertaintyType.TYPE_A:
                    return self.value
                # Type B: divide half-width by distribution divisor
                if self.distribution == Distribution.NORMAL:
                    return self.value / self.coverage_factor
                return self.value / _DIVISORS[self.distribution]

            @property
            def contribution(self) -> float:
                """cᵢ · u(xᵢ) — weighted contribution to the combined uncertainty."""
                return self.sensitivity * self.standard_uncertainty


        @dataclass
        class UncertaintyBudget:
            """Collection of components producing a combined + expanded uncertainty."""
            measurand: str
            unit: str
            components: list[UncertaintyComponent] = field(default_factory=list)
            coverage_factor: float = 2.0   # k for the final U (typically 2 → ~95% confidence)

            def add(self, component: UncertaintyComponent) -> "UncertaintyBudget":
                self.components.append(component)
                return self

            @property
            def combined_uncertainty(self) -> float:
                """u_c = √Σ(cᵢ·uᵢ)²."""
                return sqrt(sum(c.contribution ** 2 for c in self.components))

            @property
            def expanded_uncertainty(self) -> float:
                """U = k · u_c."""
                return self.coverage_factor * self.combined_uncertainty

            def as_dict(self) -> dict:
                return {
                    "measurand": self.measurand,
                    "unit": self.unit,
                    "components": [
                        {
                            "name": c.name,
                            "type": c.type.value,
                            "distribution": c.distribution.value,
                            "value": c.value,
                            "standard_uncertainty": c.standard_uncertainty,
                            "sensitivity": c.sensitivity,
                            "contribution": c.contribution,
                            "source": c.source,
                        }
                        for c in self.components
                    ],
                    "combined_uncertainty": self.combined_uncertainty,
                    "coverage_factor": self.coverage_factor,
                    "expanded_uncertainty": self.expanded_uncertainty,
                }


        # Example usage:
        #   budget = UncertaintyBudget(measurand="pressure", unit="bar")
        #   budget.add(UncertaintyComponent("reference_std_U", 0.02, type=UncertaintyType.TYPE_B,
        #                                   distribution=Distribution.NORMAL, coverage_factor=2.0,
        #                                   source="calibration certificate"))
        #   budget.add(UncertaintyComponent("repeatability", 0.015, type=UncertaintyType.TYPE_A,
        #                                   source="10-point repeat measurement"))
        #   budget.add(UncertaintyComponent("resolution", 0.005, distribution=Distribution.RECTANGULAR))
        #   U = budget.expanded_uncertainty  # → ≈0.050 bar (k=2)
    ''')
