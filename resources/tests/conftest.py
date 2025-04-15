import pytest
from survivors.models import Survivor
from resources.models import InventoryItem


@pytest.fixture
def create_survivor(db):
    def _create_survivor(**kwargs):
        default_data = {
            "name": "Default Name",
            "age": 30,
            "gender": "F",
            "latitude": 0.0,
            "longitude": 0.0,
        }
        default_data.update(kwargs)
        return Survivor.objects.create(**default_data)
    return _create_survivor


@pytest.fixture
def create_inventory_item(db):
    def _create_inventory_item(**kwargs):
        # Requires `survivor` and `item` at minimum
        assert 'survivor' in kwargs, "Missing 'survivor' argument"
        assert 'item' in kwargs, "Missing 'item' argument"
        default_data = {
            "quantity": 1,
        }
        default_data.update(kwargs)
        return InventoryItem.objects.create(**default_data)
    return _create_inventory_item
