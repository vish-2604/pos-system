# Generated by Django 5.1.6 on 2025-03-06 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0010_alter_staff_date_joined'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='date_joined',
            field=models.DateField(blank=True, null=True),
        ),
    ]
