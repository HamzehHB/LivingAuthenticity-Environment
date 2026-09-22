"""Controlled execution boundary (single CREATE to staging only).

Consumes an explicit approval plus a fresh CP16 revalidation result
path; performs exactly one staging write for CREATE. No batch, no
retry, no background work, no authoritative placement.
"""
from .executor import ControlledExecutor, execute_create
from .outcome import ExecutionResult

__all__ = ("ControlledExecutor", "ExecutionResult", "execute_create")
