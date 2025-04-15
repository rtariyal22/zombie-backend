import pytest

from resources.forms import TradeForm
from resources.models import Item


@pytest.mark.django_db
class TestTradeFormValidation:

    def test_valid_payload(self, create_survivor):
        alice = create_survivor(name="Alice", age=28, gender="F")
        bob = create_survivor(name="Bob", age=35, gender="M", latitude=2.0)
        water = Item.objects.get(name="Water")
        food = Item.objects.get(name="Food")
        data = {
            "survivor_a": alice.pk,
            "survivor_b": bob.pk,
            "items_a": [{"item": water.name, "quantity": 1}],
            "items_b": [{"item": food.name, "quantity": 1}],
        }
        form = TradeForm(data=data)
        assert form.is_valid()

    def test_empty_payload_invalid(self):
        form = TradeForm(data={})
        assert not form.is_valid()
        assert "survivor_a" in form.errors

    def test_partial_data_invalid(self):
        form = TradeForm(data={"survivor_a": 1})
        assert not form.is_valid()

    def test_invalid_types(self):
        data = {
            "survivor_a": "a",
            "survivor_b": "b",
            "items_a": [],
            "items_b": []
        }
        form = TradeForm(data=data)
        assert not form.is_valid()
