# Generated by Django 5.0.6 on 2024-11-18 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_alter_category_options_alter_order_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='old_price',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
