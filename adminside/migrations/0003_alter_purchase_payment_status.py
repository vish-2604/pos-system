# Generated by Django 5.1.6 on 2025-03-10 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0002_purchase_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='payment_status',
            field=models.CharField(choices=[('Done', 'Done'), ('Pending', 'Pending')], default='Pending', max_length=10),
        ),
    ]
