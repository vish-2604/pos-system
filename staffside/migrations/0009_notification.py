# Generated by Django 5.1.6 on 2025-03-20 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffside', '0008_order_image_urls'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
