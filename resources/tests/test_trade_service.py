from django.urls import reverse
import pytest
from resources.models import InventoryItem, Item
from resources.interface import TradeService
from resources.exceptions import TradeError


@pytest.mark.django_db
class TestTradeService:

    @pytest.fixture(autouse=True)
    def setup(self, create_survivor, create_inventory_item):
        self.alice = create_survivor(name="Alice", age=28, gender="F")
        self.bob = create_survivor(name="Bob", age=35, gender="M", latitude=2.0)
        self.item_a = Item.objects.get(name="Medication")
        self.item_b = Item.objects.get(name="Food")
        self.inventory_a = create_inventory_item(
            survivor=self.alice, item=self.item_a, quantity=5)
        self.inventory_b = create_inventory_item(
            survivor=self.bob, item=self.item_b, quantity=5)

    def test_trade_point_mismatch_raises_error(self):
        trade = TradeService(
            survivor_a_id=self.alice.id,
            survivor_b_id=self.bob.id,
            items_a=[{"item": self.inventory_b.item.name, "quantity": 3}],
            items_b=[{"item": self.inventory_a.item.name, "quantity": 3}],
        )
        with pytest.raises(TradeError, match="Unequal point value."):
            trade.execute()

    def test_trade_successful_service(self):
        trade = TradeService(
            survivor_a_id=self.alice.id,
            survivor_b_id=self.bob.id,
            items_a=[{"item": self.inventory_b.item.name, "quantity": 2}],
            items_b=[{"item": self.inventory_a.item.name, "quantity": 3}],
        )
        trade.execute()
        assert InventoryItem.objects.get(survivor=self.alice, item=self.item_b).quantity == 2
        assert InventoryItem.objects.get(survivor=self.bob, item=self.item_a).quantity == 3

    def test_successful_trade_endpoint(self, client, create_inventory_item):
        self.inventory_b = create_inventory_item(
            survivor=self.bob, item=self.item_a, quantity=5)
        payload = {
            "survivor_a": self.alice.id,
            "survivor_b": self.bob.id,
            "items_a": [{"item": self.item_b.name, "quantity": 2}],
            "items_b": [{"item": self.item_a.name, "quantity": 3}],
        }

        response = client.patch(
            reverse("trade-items"),
            data=payload,
            content_type="application/json"
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Trade completed"

        alice_has_food = InventoryItem.objects.get(
            survivor=self.alice,
            item=self.item_b,
        )
        bob_has_water = InventoryItem.objects.get(
            survivor=self.bob,
            item=self.item_a,
        )
        assert alice_has_food.quantity == 2
        assert bob_has_water.quantity == 8
