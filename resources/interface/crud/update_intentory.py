from functools import cache

from django.db import IntegrityError
from django.db.models import F

from resources.exceptions import TradeError
from resources.models import InventoryItem, Item


def transfer_items(
    giver_id: int,
    receiver_id: int,
    shopping_list: list[dict[str, int | str]],
) -> None:
    """
    Transfers specified items from one survivor to another.
    """
    try:
        for shopping_item in shopping_list:
            item_name = shopping_item["item"]
            quantity = shopping_item["quantity"]
            # Remove from giver
            InventoryItem.objects.filter(
                survivor_id=giver_id,
                item__name=item_name
            ).update(quantity=F('quantity') - quantity)

            # Add to receiver
            inventory, _ = InventoryItem.objects.get_or_create(
                survivor_id=receiver_id,
                item=items_map()[item_name]
            )
            inventory.quantity += quantity
            inventory.save()
    except IntegrityError:
        raise TradeError("Not enough resource to trade.")


@cache
def items_map() -> dict[str, Item]:
    """
    Returns a list of all items.
    """
    return {item.name: item for item in Item.objects.all()}
