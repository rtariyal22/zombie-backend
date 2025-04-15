from django.db import models
from django.db.models import Q

from survivors.models import Survivor


class Item(models.Model):
    name = models.CharField(max_length=50, unique=True)
    point_value = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.point_value} pts)"


class InventoryItem(models.Model):
    survivor = models.ForeignKey(Survivor, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('survivor', 'item')
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gte=0),
                name='quantity_non_negative',
            )
        ]

    def __str__(self):
        return f"{self.survivor.name} - {self.item.name}: {self.quantity}"
