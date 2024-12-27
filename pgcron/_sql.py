"""Internal module for SQL utilities."""

from __future__ import annotations


def escape_sql(sql: str | bytes) -> str | bytes:
    """Escape with $$ and $$ to avoid issues with quotation/special characters."""
    if isinstance(sql, bytes):
        return b"$$" + sql + b"$$"
    return f"$${sql}$$"


def is_escaped(sql: str | bytes) -> bool:
    """Check if a string is escaped with $$ and $$."""
    if isinstance(sql, bytes):
        return sql.startswith(b"$$") and sql.endswith(b"$$")
    return sql.startswith("$$") and sql.endswith("$$")
