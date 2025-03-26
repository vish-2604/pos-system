# Generated by Django 5.1.7 on 2025-03-26 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0019_alter_purchase_supplier'),
        ('staffside', '0017_sales_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='adminside.branch'),
        ),
    ]
