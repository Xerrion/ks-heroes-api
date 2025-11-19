"""Base repository with common database operation patterns."""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, cast

from postgrest.types import CountMethod
from pydantic import BaseModel

from supabase import Client

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Base repository providing common database operations.

    Eliminates boilerplate for common patterns:
    - Casting response data
    - Single item lookups
    - List operations
    - Pydantic model validation
    """

    def __init__(self, client: Client, table_name: str, model_class: Type[T]):
        """Initialize repository.

        Args:
            client: Supabase client instance
            table_name: Name of the database table
            model_class: Pydantic model class for validation
        """
        self.client = client
        self.table_name = table_name
        self.model_class = model_class

    def _cast_response(self, response: Any) -> List[Dict[str, Any]]:
        """Cast Supabase response data to typed list.

        Args:
            response: Supabase query response

        Returns:
            Typed list of dictionaries
        """
        return cast(List[Dict[str, Any]], response.data or [])

    def _to_model(self, data: Dict[str, Any]) -> T:
        """Convert dictionary to Pydantic model.

        Args:
            data: Raw database record

        Returns:
            Validated Pydantic model instance
        """
        return self.model_class.model_validate(data)

    def _to_models(self, data: List[Dict[str, Any]]) -> List[T]:
        """Convert list of dictionaries to Pydantic models.

        Args:
            data: List of raw database records

        Returns:
            List of validated Pydantic model instances
        """
        return [self._to_model(item) for item in data]

    def get_all(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "id",
        limit: Optional[int] = None,
    ) -> List[T]:
        """Get all records with optional filtering.

        Args:
            filters: Dictionary of field->value filters (eq operations)
            order_by: Column to order results by
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        query = self.client.table(self.table_name).select("*").order(order_by)

        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.eq(field, value)

        if limit:
            query = query.limit(limit)

        response = query.execute()
        data = self._cast_response(response)
        return self._to_models(data)

    def get_by_id(self, id_field: str, id_value: Any) -> Optional[T]:
        """Get single record by ID field.

        Args:
            id_field: Name of the ID column
            id_value: Value to match

        Returns:
            Model instance or None if not found
        """
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq(id_field, id_value)
            .execute()
        )

        data = self._cast_response(response)
        if data:
            return self._to_model(data[0])
        return None

    def get_filtered(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, tuple]] = None,
        order_by: str = "id",
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> tuple[List[T], int]:
        query = (
            self.client.table(self.table_name)
            .select("*", count=CountMethod.exact)
            .order(order_by)
        )

        # Apply equality filters
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.eq(field, value)

        # Apply range filters
        if range_filters:
            for field, (min_val, max_val) in range_filters.items():
                if min_val is not None:
                    query = query.gte(field, min_val)
                if max_val is not None:
                    query = query.lte(field, max_val)

        # Apply pagination
        if limit:
            upper_bound = max(offset + limit - 1, offset)
            query = query.range(offset, upper_bound)

        response = query.execute()
        data = self._cast_response(response)
        total = int(response.count or 0)

        return self._to_models(data), total
