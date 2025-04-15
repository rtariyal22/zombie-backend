from django import forms
from survivors.models import Survivor
from resources.models import Item


class TradeForm(forms.Form):
    survivor_a = forms.IntegerField()
    survivor_b = forms.IntegerField()
    items_a = forms.JSONField()
    items_b = forms.JSONField()

    def clean(self) -> dict:
        cleaned_data = super().clean()
        survivor_a_id = cleaned_data.get('survivor_a')
        survivor_b_id = cleaned_data.get('survivor_b')

        if survivor_a_id == survivor_b_id:
            raise forms.ValidationError('Survivors must be different.')

        try:
            cleaned_data['survivor_a_obj'] = Survivor.objects.get(
                id=survivor_a_id)
        except Survivor.DoesNotExist:
            raise forms.ValidationError('Survivor A does not exist.')

        try:
            cleaned_data['survivor_b_obj'] = Survivor.objects.get(
                id=survivor_b_id)
        except Survivor.DoesNotExist:
            raise forms.ValidationError('Survivor B does not exist.')

        cleaned_data['items_a_obj'] = self._validate_items(
            cleaned_data.get('items_a', []), 'A')
        cleaned_data['items_b_obj'] = self._validate_items(
            cleaned_data.get('items_b', []), 'B')

        return cleaned_data

    @staticmethod
    def _validate_items(item_list, label):
        if not isinstance(item_list, list):
            raise forms.ValidationError(f'items_{label} must be a list of objects')

        item_names = {entry.get('item') for entry in item_list}
        if None in item_names:
            raise forms.ValidationError(
                f'All entries in items_{label} must have an "item" key')

        items_lookup = {item.name: item for item in
                        Item.objects.filter(name__in=item_names)}

        unknown_items = item_names - items_lookup.keys()
        if unknown_items:
            raise forms.ValidationError(
                f'Invalid items in items_{label}: {", ".join(unknown_items)}')

        valid_items = []
        for entry in item_list:
            item_name = entry['item']
            quantity = entry.get('quantity')

            if not isinstance(quantity, int) or quantity < 1:
                raise forms.ValidationError(
                    f'Quantity for item "{item_name}" in items_{label} must be a positive integer.')
            valid_items.append({
                "item": items_lookup[item_name],
                "quantity": quantity
            })
        return valid_items
