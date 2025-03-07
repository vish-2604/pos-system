# Generated by Django 5.1.6 on 2025-03-06 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0003_alter_categories_categories_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staff',
            old_name='staff_firstname',
            new_name='staff_fullname',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='staff_lastname',
        ),
        migrations.AddField(
            model_name='staff',
            name='staff_password',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='staff',
            name='staff_email',
            field=models.EmailField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='staff',
            name='staff_username',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
