"""
Query builder utilities for common database query patterns.

This module provides reusable functions for building SQLAlchemy queries
with common patterns like sorting, filtering, and pagination.
"""

from typing import Optional, Literal, TypeVar, Generic, List, Tuple, Any
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc

T = TypeVar("T")


class QueryBuilder(Generic[T]):
    """Builder for SQLAlchemy queries with common patterns."""

    def __init__(self, query: Query[T]):
        """
        Initialize query builder.

        Args:
            query: Base SQLAlchemy query
        """
        self.query = query

    def apply_sorting(
        self,
        sort_by: Optional[str],
        order: Optional[Literal["asc", "desc"]],
        default_sort: str = "updated_at",
        default_order: Literal["asc", "desc"] = "desc",
        sortable_fields: Optional[dict[str, Any]] = None,
    ) -> "QueryBuilder[T]":
        """
        Apply sorting to query.

        Args:
            sort_by: Field to sort by
            order: Sort order (asc, desc)
            default_sort: Default field to sort by if sort_by is None
            default_order: Default order if order is None
            sortable_fields: Dictionary mapping field names to SQLAlchemy columns

        Returns:
            Self for method chaining
        """
        if sort_by and sortable_fields:
            if sort_by in sortable_fields:
                column = sortable_fields[sort_by]
                # Default order: desc for updated_at, asc for others
                if order is None:
                    order = "desc" if sort_by == "updated_at" else "asc"

                if order == "desc":
                    self.query = self.query.order_by(desc(column))
                else:
                    self.query = self.query.order_by(asc(column))
            else:
                # Invalid sort_by, use default
                sort_by = default_sort
                order = default_order
        else:
            # Use default sorting
            if sortable_fields and default_sort in sortable_fields:
                column = sortable_fields[default_sort]
                if default_order == "desc":
                    self.query = self.query.order_by(desc(column))
                else:
                    self.query = self.query.order_by(asc(column))

        return self

    def apply_pagination(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[T], int]:
        """
        Apply pagination to query and return results with total count.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (results, total_count)
        """
        total = self.query.count()
        results = self.query.offset(offset).limit(limit).all()
        return results, total

    def build(self) -> Query[T]:
        """Get the built query."""
        return self.query
