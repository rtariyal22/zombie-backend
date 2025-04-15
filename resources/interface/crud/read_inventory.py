from django.db.models import QuerySet

from resources.models import InventoryItem


def fetch_and_lock_inventory_items(
    survivor_ids: list[int],
    items: list[str],
) -> QuerySet[InventoryItem]:
    return InventoryItem.objects.select_for_update().filter(
        survivor_id__in=survivor_ids,
        survivor__is_infected=False,
        item__name__in=items,
        quantity__gt=0,
    ).select_related('item')
