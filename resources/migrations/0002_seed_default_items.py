from django.db import migrations


def seed_items(apps, schema_editor):
    Item = apps.get_model('resources', 'Item')
    items = [
        ("Water", 4),
        ("Food", 3),
        ("Medication", 2),
        ("Ammunition", 1),
    ]
    for name, points in items:
        Item.objects.get_or_create(name=name, point_value=points)


def remove_items(apps, schema_editor):
    Item = apps.get_model('resources', 'Item')
    item_names = ["Water", "Food", "Medication", "Ammunition"]
    Item.objects.filter(name__in=item_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_items, reverse_code=remove_items),
    ]
