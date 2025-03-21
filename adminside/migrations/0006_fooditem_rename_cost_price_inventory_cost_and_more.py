# Generated by Django 5.1.6 on 2025-03-11 06:44

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0005_alter_categories_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('price', models.IntegerField()),
                ('description', models.TextField(max_length=100)),
                ('quantity', models.IntegerField(default=1)),
            ],
        ),
        migrations.RenameField(
            model_name='inventory',
            old_name='cost_price',
            new_name='cost',
        ),
        migrations.RenameField(
            model_name='inventory',
            old_name='food_item_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='inventory',
            old_name='food_item_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='inventory',
            old_name='sell_price',
            new_name='price',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='quantity',
        ),
        migrations.AddField(
            model_name='inventory',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='stock',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='inventory',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminside.supplier'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminside.branch'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminside.categories'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='exp_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='mfg_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
