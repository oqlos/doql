"""nlp2doql — Natural language → DOQL (.doql.less) specifications."""

from nlp2doql.models import BlockPlan, DoqlPlan, GenerateResult
from nlp2doql.pipeline import generate_spec

__version__ = "1.0.37"
__all__ = [
    "BlockPlan",
    "DoqlPlan",
    "GenerateResult",
    "generate_spec",
    "__version__",
]
