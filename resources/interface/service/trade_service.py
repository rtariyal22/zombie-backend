from collections import defaultdict
from django.db.transaction import atomic
from django.utils.functional import cached_property

from resources.exceptions import TradeError
from resources.interface import (
    fetch_and_lock_inventory_items,
    infected_survivors,
    transfer_items,
)
from django.core.cache import cache

from survivors.models import Survivor

SURVIVOR_CACHE_KEY = 'survivor_cache_key'


class TradeService:
    """
    Coordinates the item trading process between two survivors.
    This service acts as the main orchestrator that delegates to
    specialized services for survivor infection checks, inventory
    validation, item transfer, and trade validation.
    Attributes:
        survivor_a_id (int): ID of the first survivor.
        survivor_b_id (int): ID of the second survivor.
        items_a (list): Items to be traded from survivor A.
        items_b (list): Items to be traded from survivor B.
    Methods:
        execute():
            Executes the complete trade transaction in an atomic block.
    """
    def __init__(
        self,
        survivor_a_id: int,
        survivor_b_id: int,
        items_a: list[dict[str, int]],
        items_b: list[dict[str, int]],
    ) -> None:
        self.survivor_a_id = survivor_a_id
        self.survivor_b_id = survivor_b_id
        self.items_a = items_a
        self.items_b = items_b

        self.health_service = SurvivorHealthService([survivor_a_id, survivor_b_id])
        self.inventory_service = InventoryService({
            survivor_a_id: items_a,
            survivor_b_id: items_b
        })
        self.trade_validator = TradeValidatorService(
            self.inventory_service,
            survivor_a_id, survivor_b_id, items_a, items_b
        )
        self.transfer_service = ItemTransferService(
            survivor_a_id, survivor_b_id, items_a, items_b
        )

    @atomic
    def execute(self) -> None:
        self.health_service.validate_not_infected_from_cache()
        self.trade_validator.validate()
        self.transfer_service.transfer()
        # Check for infection after trade to ensure no survivor is infected
        # during the trade process. If any survivor is infected, rollback
        # the transaction.
        self.health_service.validate_not_infected_live()


class SurvivorHealthService:
    """
    Handles health state validations for survivors involved in a trade.
    Provides methods to check if survivors are infected either from
    cache (for performance) or via a live query (for accuracy).
    Attributes:
        survivor_ids (List[int]): List of survivor IDs to validate.
    Methods:
        validate_not_infected_from_cache():
            Raises TradeError if any survivor is marked as infected in cache.
        validate_not_infected_live():
            Performs live validation; updates cache and raises TradeError if infected.
    """
    def __init__(self, survivor_ids: list[int]) -> None:
        self.survivor_ids = survivor_ids

    def validate_not_infected_from_cache(self) -> None:
        for survivor_id in self.survivor_ids:
            if cache.get(f'{SURVIVOR_CACHE_KEY}_{survivor_id}'):
                raise TradeError(f'Survivor {survivor_id} is infected.')

    def validate_not_infected_live(self) -> None:
        if infected_list := list(infected_survivors(self.survivor_ids)):
            self._update_cache(infected_list)
            raise TradeError('Infected survivors cannot trade.')

    @staticmethod
    def _update_cache(infected_list: list[Survivor]) -> None:
        for infected in infected_list:
            cache_key = f'{SURVIVOR_CACHE_KEY}_{infected.pk}'
            cache.set(cache_key, infected, timeout=None)


class InventoryService:
    """
    Responsible for fetching and validating inventory items for multiple survivors.
    Provides methods to validate item availability and calculate trade point totals.
    Attributes:
        survivor_items_map (dict): Mapping of survivor IDs to items they intend to trade.
    Properties:
        inventories (dict): dictionary of inventories per survivor.
    Methods:
        validate_inventory():
            Validates if all survivors have enough inventory to perform the trade.
        calculate_points(survivor_id, items):
            Calculates total point value of items a survivor wants to trade.
    """
    def __init__(self, survivor_items_map: dict) -> None:
        self.survivor_items_map = survivor_items_map  # {id: items}

    @cached_property
    def inventories(self) -> dict:
        result = defaultdict(dict)
        survivor_ids = []
        traded_items = []
        for survivor_id, items in self.survivor_items_map.items():
            survivor_ids.append(survivor_id)
            traded_items.extend([i['item'] for i in items])
        inventories = fetch_and_lock_inventory_items(survivor_ids, traded_items)
        for inventory in inventories:
            result[inventory.survivor.pk][inventory.item.name] = inventory
        return result

    def calculate_points(
        self,
        survivor_id: int,
        items: list[dict[str, int]],
    ) -> int:
        try:
            return sum(
                self.inventories[survivor_id][i["item"]].item.point_value * i["quantity"]
                for i in items
            )
        except KeyError as e:
            raise TradeError(f"Item {e} not found in survivor {survivor_id}'s inventory.")


class ItemTransferService:
    """
    Facilitates the transfer of items between two survivors.
    Uses pre-fetched inventory to move items from one survivor to another,
    delegating to the low-level `transfer_items` interface function.
    Attributes:
        survivor_a_id (int): ID of the first survivor.
        survivor_b_id (int): ID of the second survivor.
        items_a (list): Items being sent by survivor A.
        items_b (list): Items being sent by survivor B.
    Methods:
        transfer():
            Executes the bidirectional item transfer between survivors.
    """
    def __init__(
        self,
        survivor_a_id: int,
        survivor_b_id: int,
        items_a: list[dict[str, int]],
        items_b: list[dict[str, int]],
    ) -> None:
        self.survivor_a_id = survivor_a_id
        self.survivor_b_id = survivor_b_id
        self.items_a = items_a
        self.items_b = items_b

    def transfer(self) -> None:
        transfer_items(
            giver_id=self.survivor_a_id,
            receiver_id=self.survivor_b_id,
            shopping_list=self.items_b,
        )
        transfer_items(
            giver_id=self.survivor_b_id,
            receiver_id=self.survivor_a_id,
            shopping_list=self.items_a,
        )


class TradeValidatorService:
    """
    Validates that a trade is fair and feasible before execution.
    Checks that the point value of traded items is equal and that
    all items exist in sufficient quantity in each survivor's inventory.
    Attributes:
        inventory_service (InventoryService): Shared inventory service instance.
        survivor_a_id (int): ID of the first survivor.
        survivor_b_id (int): ID of the second survivor.
        items_a (list): Items to be traded by survivor A.
        items_b (list): Items to be traded by survivor B.
    Methods:
        validate():
            Ensures equal point value and sufficient inventory availability.
    """
    def __init__(
        self,
        inventory_service: InventoryService,
        survivor_a_id: int,
        survivor_b_id: int,
        items_a: list[dict[str, int]],
        items_b: list[dict[str, int]],
    ) -> None:
        self.inventory_service = inventory_service
        self.survivor_a_id = survivor_a_id
        self.survivor_b_id = survivor_b_id
        self.items_a = items_a
        self.items_b = items_b

    def validate(self) -> None:
        total_a = self.inventory_service.calculate_points(self.survivor_b_id, self.items_a)
        total_b = self.inventory_service.calculate_points(self.survivor_a_id, self.items_b)
        if total_a != total_b:
            raise TradeError('Unequal point value.')
