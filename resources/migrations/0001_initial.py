# Generated by Django 5.2 on 2025-04-11 15:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('survivors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('point_value', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('survivor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivors.survivor')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resources.item')),
            ],
            options={
                'constraints': [models.CheckConstraint(condition=models.Q(('quantity__gte', 0)), name='quantity_non_negative')],
                'unique_together': {('survivor', 'item')},
            },
        ),
    ]
