# Generated by Django 5.0.6 on 2024-09-25 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_invoice_email_remove_invoice_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='product_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
