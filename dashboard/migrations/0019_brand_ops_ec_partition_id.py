# Generated by Django 3.1.2 on 2020-11-18 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_brand_program_website_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand_ops',
            name='ec_partition_id',
            field=models.CharField(blank='False', max_length=20, null='False'),
            preserve_default='False',
        ),
    ]
