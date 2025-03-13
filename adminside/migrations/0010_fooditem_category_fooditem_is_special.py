# Generated by Django 5.1.6 on 2025-03-12 04:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0009_alter_customer_customer_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminside.categories'),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='is_special',
            field=models.BooleanField(default=False),
        ),
    ]
