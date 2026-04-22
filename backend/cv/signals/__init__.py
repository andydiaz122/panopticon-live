"""Biomechanical signal extractors for PANOPTICON LIVE.

All 7 concrete extractors inherit from BaseSignalExtractor and implement the
symmetric target/opponent API per USER-CORRECTION-013. The FeatureCompiler
in backend/cv/compiler.py orchestrates per-tick dispatch with the
compiler-flush contract (USER-CORRECTION-018).
"""

from backend.cv.signals.base import BaseSignalExtractor
from backend.cv.signals.baseline_retreat import BaselineRetreat
from backend.cv.signals.crouch_depth import CrouchDepth
from backend.cv.signals.lateral_work_rate import LateralWorkRate
from backend.cv.signals.recovery_latency import RecoveryLatency
from backend.cv.signals.ritual_entropy import RitualEntropy
from backend.cv.signals.serve_toss_variance import ServeTossVariance
from backend.cv.signals.split_step_latency import SplitStepLatency

__all__ = [
    "BaseSignalExtractor",
    "BaselineRetreat",
    "CrouchDepth",
    "LateralWorkRate",
    "RecoveryLatency",
    "RitualEntropy",
    "ServeTossVariance",
    "SplitStepLatency",
]

ALL_EXTRACTOR_CLASSES: tuple[type[BaseSignalExtractor], ...] = (
    LateralWorkRate,
    RecoveryLatency,
    SplitStepLatency,
    ServeTossVariance,
    RitualEntropy,
    CrouchDepth,
    BaselineRetreat,
)
"""Canonical ordered tuple of the 7 extractor classes.

The FeatureCompiler instantiates each twice (target='A', 'B') = 14 instances.
Order is stable so that SignalSample emission ordering within a tick is
deterministic — useful for testing.
"""
