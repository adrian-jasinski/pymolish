"""Helpers for normalizing arguments arriving from the PyMOL command line."""

from __future__ import annotations


def clean(value: str) -> str:
    """Strip one layer of surrounding quotes from a PyMOL command argument.

    PyMOL passes arguments through as raw strings, sometimes still wrapped in the
    quotes the user typed. Non-strings are returned untouched.
    """
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")
