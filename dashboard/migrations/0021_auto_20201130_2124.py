# Generated by Django 3.1.3 on 2020-11-30 21:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0020_auto_20201130_2123'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brand_ops',
            old_name='bem_inaccurate_selection',
            new_name='bem_attribute_count',
        ),
        migrations.RenameField(
            model_name='brand_ops',
            old_name='bem_key_count',
            new_name='validation_inaccurate_selection',
        ),
        migrations.RenameField(
            model_name='brand_ops',
            old_name='bem_sample_selection',
            new_name='validation_sample_selection',
        ),
    ]