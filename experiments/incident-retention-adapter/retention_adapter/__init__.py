"""Experimental offline retention statements, separate from deletion evidence."""

DOMAIN = "incident-retention-adapter/0.1"
VERSION = "0.1.0"

from .core import InputError, assess, signing_bytes

__all__ = ["InputError", "assess", "signing_bytes"]
