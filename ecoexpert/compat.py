"""Adaptación de frozendict 1.2, explícita y limitada al proceso."""
import collections
from collections.abc import Mapping

if not hasattr(collections, "Mapping"):
    collections.Mapping = Mapping
