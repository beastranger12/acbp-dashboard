# Generated by Django 3.1.2 on 2020-11-05 00:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_auto_20201105_0018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brand_program',
            name='website_id',
        ),
    ]
