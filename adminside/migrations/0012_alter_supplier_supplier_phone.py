# Generated by Django 5.1.6 on 2025-03-12 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0011_remove_supplier_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='supplier_phone',
            field=models.CharField(max_length=10),
        ),
    ]
