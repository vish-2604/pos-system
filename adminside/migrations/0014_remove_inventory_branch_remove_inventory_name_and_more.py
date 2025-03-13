# Generated by Django 5.1.6 on 2025-03-12 07:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0013_purchase_branch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='branch',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='name',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='supplier',
        ),
        migrations.AddField(
            model_name='inventory',
            name='purchase',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='inventory_items', to='adminside.purchase'),
            preserve_default=False,
        ),
    ]
