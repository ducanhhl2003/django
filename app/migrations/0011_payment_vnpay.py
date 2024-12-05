# Generated by Django 5.0.6 on 2024-09-26 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_invoice_product_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment_VNPay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.IntegerField(default=0, null=True)),
                ('amount', models.FloatField(blank=True, default=0.0, null=True)),
                ('order_desc', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
