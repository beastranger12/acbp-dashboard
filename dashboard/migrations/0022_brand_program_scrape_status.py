# Generated by Django 3.1.3 on 2020-11-30 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_auto_20201130_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand_program',
            name='scrape_status',
            field=models.CharField(blank='False', max_length=20, null='False'),
            preserve_default='False',
        ),
    ]