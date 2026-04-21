"""Panopticon Live — biomechanical intelligence for pro tennis.

Built for the Anthropic x Cerebral Valley "Built with Opus 4.7" hackathon (April 2026).

Module layout:
- backend.config      — environment + device selection
- backend.cv          — YOLO inference, Kalman, state machine, signal extractors
- backend.db          — DuckDB schema + Pydantic v2 data contracts
- backend.agents      — Opus 4.7 Reasoner/Designer/Voice + Haiku narrator + Managed Agents
- backend.api         — FastAPI SSE replay endpoints + Opus orchestration
- backend.precompute  — CLI entry point for offline clip processing
"""

__version__ = "0.1.0"
