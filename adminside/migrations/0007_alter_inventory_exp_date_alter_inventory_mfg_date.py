# Generated by Django 5.1.6 on 2025-03-11 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0006_fooditem_rename_cost_price_inventory_cost_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='exp_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='mfg_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
