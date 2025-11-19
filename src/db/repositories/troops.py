"""Repository for troops data access."""

from typing import Any, Dict, List, Optional

from src.db.repository_base import BaseRepository
from src.schemas.troops import Troop, TroopType
from supabase import Client


class TroopsRepository(BaseRepository[Troop]):
    """Repository for managing troops data."""

    def __init__(self, client: Client):
        """Initialize Troops repository with Supabase client.

        Args:
            client: Supabase client instance
        """
        super().__init__(client, "troops", Troop)

    def get_all(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "troop_type",
        limit: Optional[int] = None,
        troop_type: Optional[TroopType] = None,
        min_level: int = 1,
        max_level: int = 10,
        min_tg: int = 0,
        max_tg: int = 5,
    ) -> List[Troop]:
        """Get all troops with optional filtering and enrichment data.

        Args:
            filters: Direct equality filters (field -> value)
            order_by: Column to order results by (default: troop_type)
            limit: Maximum number of rows to return
            troop_type: Filter by Infantry/Cavalry/Archer
            min_level: Minimum troop level (default 1)
            max_level: Maximum troop level (default 10)
            min_tg: Minimum True Gold level (default 0)
            max_tg: Maximum True Gold level (default 5)

        Returns:
            List of troop configurations enriched with training data
        """

        level_min = min(min_level, max_level)
        level_max = max(min_level, max_level)
        tg_min = min(min_tg, max_tg)
        tg_max = max(min_tg, max_tg)

        query = self.client.table(self.table_name).select("*")

        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.eq(field, value)

        if troop_type:
            query = query.eq("troop_type", troop_type.value)

        query = query.gte("troop_level", level_min).lte("troop_level", level_max)
        query = query.gte("true_gold_level", tg_min).lte("true_gold_level", tg_max)

        primary_order = order_by or "troop_type"
        query = query.order(primary_order).order("troop_level").order("true_gold_level")

        if limit:
            query = query.limit(limit)

        response = query.execute()
        data = self._cast_response(response)

        for troop in data:
            self._enrich_troop_data(troop)

        return self._to_models(data)

    def get_by_configuration(
        self, troop_type: TroopType, troop_level: int, true_gold_level: int = 0
    ) -> Optional[Troop]:
        """Get specific troop configuration including enrichment data.

        Args:
            troop_type: Infantry, Cavalry, or Archer
            troop_level: Troop level (1-11)
            true_gold_level: True Gold tier (0-10)

        Returns:
            Troop data or None if not found
        """

        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("troop_type", troop_type.value)
            .eq("troop_level", troop_level)
            .eq("true_gold_level", true_gold_level)
            .limit(1)
            .execute()
        )

        records = self._cast_response(response)
        if not records:
            return None

        troop = records[0]
        self._enrich_troop_data(troop)
        return self._to_model(troop)

    def _get_enrichment_data(self, troop: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch training costs and event points for a troop entry."""

        costs_response = (
            self.client.table("troop_training_costs")
            .select("resource_id, cost")
            .eq("troop_type", troop["troop_type"])
            .eq("troop_level", troop["troop_level"])
            .execute()
        )
        costs_data = self._cast_response(costs_response)
        training_costs = {item["resource_id"]: item["cost"] for item in costs_data}

        events_response = (
            self.client.table("troop_event_points")
            .select("event_id, base_points")
            .eq("troop_type", troop["troop_type"])
            .eq("troop_level", troop["troop_level"])
            .execute()
        )
        events_data = self._cast_response(events_response)
        event_points = {item["event_id"]: item["base_points"] for item in events_data}

        return {"training_costs": training_costs, "event_points": event_points}

    def _enrich_troop_data(self, troop: Dict[str, Any]) -> None:
        """Attach enrichment metadata (costs/events) onto a troop record."""

        enrichment = self._get_enrichment_data(troop)
        troop.update(enrichment)
