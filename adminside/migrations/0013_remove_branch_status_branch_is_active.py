# Generated by Django 5.1.6 on 2025-03-07 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0012_remove_branch_manager_id_branch_manager_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='branch',
            name='status',
        ),
        migrations.AddField(
            model_name='branch',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
