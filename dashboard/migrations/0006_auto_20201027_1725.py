# Generated by Django 3.1.2 on 2020-10-27 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_brand_program_website_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brand_ops',
            old_name='backfill_pt_count',
            new_name='backfill_nam_dropped',
        ),
    ]