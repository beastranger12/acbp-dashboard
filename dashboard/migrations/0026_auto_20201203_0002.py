# Generated by Django 3.1.3 on 2020-12-03 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0025_auto_20201202_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand_program',
            name='incremental_sku_coverage',
            field=models.FloatField(blank='True', null='False'),
        ),
    ]