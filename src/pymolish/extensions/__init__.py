"""Extension sub-packages — one per command category.

Each sub-package defines a category label and an ``__init_plugin__(app=None)``
callable that the top-level bootstrap invokes. Phase 2 of the migration plan
populates the actual command modules; this scaffold only wires the discovery.
"""
