"""Biomechanical signal extractors.

Placeholder package — concrete extractors land in Action 3; compiler wiring in Action 3.5.
The BaseSignalExtractor ABC is the public contract every concrete signal inherits from.
"""

from backend.cv.signals.base import BaseSignalExtractor

__all__ = ["BaseSignalExtractor"]
