"""Audit / traceability record (observational only).

The audit layer records the controlled lifecycle
(proposal -> approval -> revalidation -> execution) for inspection.
It never approves, authorizes, executes, or mutates knowledge.
"""
from .outcome import AuditRecord, build_audit_record, record_audit_for_execution

__all__ = ("AuditRecord", "build_audit_record", "record_audit_for_execution")
