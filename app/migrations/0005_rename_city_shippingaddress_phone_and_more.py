# Generated by Django 5.0.6 on 2024-09-25 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_category_product_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='city',
            new_name='phone',
        ),
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='mobile',
            new_name='typepayment',
        ),
        migrations.RemoveField(
            model_name='shippingaddress',
            name='state',
        ),
    ]
