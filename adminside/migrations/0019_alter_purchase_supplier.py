# Generated by Django 5.1.7 on 2025-03-26 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0018_staff_is_staff_alter_staff_is_superuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminside.supplier'),
        ),
    ]
