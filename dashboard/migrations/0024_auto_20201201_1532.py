# Generated by Django 3.1.3 on 2020-12-01 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0023_brand_ops_flag_overall_website_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brand_ops',
            name='flag_overall_website_status',
        ),
        migrations.AddField(
            model_name='brand_program',
            name='flag_overall_website_status',
            field=models.CharField(blank='False', max_length=5, null='False'),
            preserve_default='False',
        ),
    ]
