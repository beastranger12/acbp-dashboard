# Generated by Django 3.1.3 on 2020-12-03 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0026_auto_20201203_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand_ops',
            name='backfill_pt_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='backfill_pt_source_attributes_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='backfill_source_attributes_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='bem_attribute_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='bs_attributes_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='bsv_attributes_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='bsv_inaccurate_selection',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='bsv_sample_selection',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='bundle_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='converted_ontology_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='parent_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='pt_request_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='ptc_selection_size',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='ptv_inaccurate_selection',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='ptv_sample_selection',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='ptv_selection_size',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='require_ontology_attributes_post_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='require_ontology_attributes_prior_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='slots_backfilled_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='validation_inaccurate_selection',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_ops',
            name='validation_sample_selection',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='idf_av_performance',
            field=models.FloatField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='idf_av_ssl_performance',
            field=models.FloatField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='incremental_matching_gv_coverage',
            field=models.FloatField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='keys_available_website_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='keys_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='matching_gv_coverage',
            field=models.FloatField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='matching_sku_coverage',
            field=models.FloatField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='mp_id',
            field=models.IntegerField(blank='True', null='False'),
        ),
        migrations.AlterField(
            model_name='brand_program',
            name='slots_backfilled_count',
            field=models.IntegerField(blank='True', null='False'),
        ),
    ]
