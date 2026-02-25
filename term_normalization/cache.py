"""
Term deduplication cache for normalization system.

This module provides thread-safe caching for normalized terms to avoid
redundant API calls and lookups across multiple files.
"""

import threading
from typing import Dict, Optional, List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from term_normalization.variant_search import VariantSearchResult
    from term_normalization.drug_search import DrugSearchResult


@dataclass
class CachedVariantResult:
    """Cached variant normalization result."""

    raw_input: str
    results: List  # List[VariantSearchResult]


@dataclass
class CachedDrugResult:
    """Cached drug normalization result."""

    raw_input: str
    results: List  # List[DrugSearchResult]


class TermCache:
    """Thread-safe cache for normalized terms."""

    def __init__(self):
        self._variant_cache: Dict[str, CachedVariantResult] = {}
        self._drug_cache: Dict[str, CachedDrugResult] = {}

    def get_variant(self, raw_variant: str) -> Optional[List]:
        """
        Get cached variant results.

        Args:
            raw_variant: Raw variant string (case-insensitive)

        Returns:
            List of VariantSearchResult if cached, None otherwise
        """
        key = raw_variant.lower().strip()
        cached = self._variant_cache.get(key)
        return cached.results if cached else None

    def set_variant(
        self, raw_variant: str, results: List
    ) -> None:
        """
        Cache variant results.

        Args:
            raw_variant: Raw variant string
            results: List of VariantSearchResult to cache
        """
        key = raw_variant.lower().strip()
        self._variant_cache[key] = CachedVariantResult(
            raw_input=raw_variant, results=results
        )

    def get_drug(self, raw_drug: str) -> Optional[List]:
        """
        Get cached drug results.

        Args:
            raw_drug: Raw drug string (case-insensitive)

        Returns:
            List of DrugSearchResult if cached, None otherwise
        """
        key = raw_drug.lower().strip()
        cached = self._drug_cache.get(key)
        return cached.results if cached else None

    def set_drug(self, raw_drug: str, results: List) -> None:
        """
        Cache drug results.

        Args:
            raw_drug: Raw drug string
            results: List of DrugSearchResult to cache
        """
        key = raw_drug.lower().strip()
        self._drug_cache[key] = CachedDrugResult(raw_input=raw_drug, results=results)

    def clear(self) -> None:
        """Clear all cached terms."""
        self._variant_cache.clear()
        self._drug_cache.clear()

    def stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache sizes
        """
        return {
            "variant_count": len(self._variant_cache),
            "drug_count": len(self._drug_cache),
        }


# Global cache instance
_TERM_CACHE = TermCache()


def get_term_cache() -> TermCache:
    """Get the global term cache instance."""
    return _TERM_CACHE


# Global PharmGKB API rate limiter (max 2 concurrent calls)
_PHARMGKB_SEMAPHORE = threading.Semaphore(2)


def get_pharmgkb_semaphore() -> threading.Semaphore:
    """
    Get the global PharmGKB API rate limiting semaphore.

    PharmGKB has rate limits, so we restrict to max 2 concurrent API calls.
    This semaphore should be acquired before making PharmGKB API requests.
    """
    return _PHARMGKB_SEMAPHORE
