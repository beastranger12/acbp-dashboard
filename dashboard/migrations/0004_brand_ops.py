# Generated by Django 3.1.2 on 2020-10-13 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_benchmark_brand_program'),
    ]

    operations = [
        migrations.CreateModel(
            name='brand_ops',
            fields=[
                ('bid', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(blank='False', max_length=200, null='False')),
                ('website', models.CharField(blank='False', max_length=200, null='False')),
                ('mp_id', models.IntegerField(blank='False', null='False')),
                ('ssl_completed_date', models.DateField(blank='True', null='True')),
                ('matching_completed_date', models.DateField(blank='True', null='True')),
                ('incremental_matching_completed_date', models.DateField(blank='True', null='True')),
                ('bs_owner', models.CharField(blank='False', max_length=50, null='False')),
                ('bs_status', models.CharField(blank='False', max_length=50, null='False')),
                ('bs_allocation_date', models.DateField(blank='True', null='True')),
                ('bs_completion_date', models.DateField(blank='True', null='True')),
                ('bsv_owner', models.CharField(blank='False', max_length=50, null='False')),
                ('bsv_status', models.CharField(blank='False', max_length=50, null='False')),
                ('bsv_allocation_date', models.DateField(blank='True', null='True')),
                ('bsv_completion_date', models.DateField(blank='True', null='True')),
                ('ptc_owner', models.CharField(blank='False', max_length=50, null='False')),
                ('ptc_status', models.CharField(blank='False', max_length=50, null='False')),
                ('ptc_allocation_date', models.DateField(blank='True', null='True')),
                ('ptc_completion_date', models.DateField(blank='True', null='True')),
                ('ptv_owner', models.CharField(blank='False', max_length=50, null='False')),
                ('ptv_status', models.CharField(blank='False', max_length=50, null='False')),
                ('ptv_allocation_date', models.DateField(blank='True', null='True')),
                ('ptv_completion_date', models.DateField(blank='True', null='True')),
                ('backfill_owner', models.CharField(blank='False', max_length=50, null='False')),
                ('backfill_status', models.CharField(blank='False', max_length=50, null='False')),
                ('backfill_allocation_date', models.DateField(blank='True', null='True')),
                ('backfill_completion_date', models.DateField(blank='True', null='True')),
                ('bem_owner', models.CharField(blank='False', max_length=50, null='False')),
                ('bem_status', models.CharField(blank='False', max_length=50, null='False')),
                ('bem_allocation_date', models.DateField(blank='True', null='True')),
                ('bem_completion_date', models.DateField(blank='True', null='True')),
                ('published_owner', models.CharField(blank='False', max_length=50, null='False')),
                ('published_status', models.CharField(blank='False', max_length=50, null='False')),
                ('published_allocation_date', models.DateField(blank='True', null='True')),
                ('published_completion_date', models.DateField(blank='True', null='True')),
                ('backfill_type', models.CharField(blank='False', max_length=50, null='False')),
                ('language', models.CharField(blank='False', max_length=50, null='False')),
                ('business_request', models.CharField(blank='False', max_length=50, null='False')),
                ('brand_iteration', models.IntegerField(blank='False', null='False')),
                ('bs_priority', models.CharField(blank='False', max_length=50, null='False')),
                ('pt_request_count', models.IntegerField(blank='False', null='False')),
                ('bs_ptname', models.CharField(blank='False', max_length=50, null='False')),
                ('bs_attributes_count', models.IntegerField(blank='False', null='False')),
                ('bs_comments', models.CharField(blank='False', max_length=50, null='False')),
                ('bs_filename', models.CharField(blank='False', max_length=50, null='False')),
                ('bs_path', models.CharField(blank='False', max_length=50, null='False')),
                ('pt_not_found', models.CharField(blank='False', max_length=50, null='False')),
                ('bsv_pt_not_found', models.IntegerField(blank='False', null='False')),
                ('bsv_attributes_count', models.IntegerField(blank='False', null='False')),
                ('bsv_comments', models.CharField(blank='False', max_length=50, null='False')),
                ('bsv_inaccurate_selection', models.IntegerField(blank='False', null='False')),
                ('bsv_sample_selection', models.IntegerField(blank='False', null='False')),
                ('ptc_selection_size', models.IntegerField(blank='False', null='False')),
                ('parent_count', models.IntegerField(blank='False', null='False')),
                ('bundle_count', models.IntegerField(blank='False', null='False')),
                ('ptc_comments', models.CharField(blank='False', max_length=50, null='False')),
                ('ptc_file_name', models.CharField(blank='False', max_length=50, null='False')),
                ('ptc_path', models.CharField(blank='False', max_length=50, null='False')),
                ('ptv_selection_size', models.IntegerField(blank='False', null='False')),
                ('ptv_comments', models.CharField(blank='False', max_length=50, null='False')),
                ('ptv_file_name', models.CharField(blank='False', max_length=50, null='False')),
                ('ptv_inaccurate_selection', models.IntegerField(blank='False', null='False')),
                ('ptv_sample_selection', models.IntegerField(blank='False', null='False')),
                ('backfill_pt_count', models.IntegerField(blank='False', null='False')),
                ('backfill_source_attributes_count', models.IntegerField(blank='False', null='False')),
                ('backfill_pt_source_attributes_count', models.IntegerField(blank='False', null='False')),
                ('backfill_comments', models.CharField(blank='False', max_length=50, null='False')),
                ('bem_attempted', models.CharField(blank='False', max_length=50, null='False')),
                ('bem_converted', models.CharField(blank='False', max_length=50, null='False')),
                ('bem_inaccurate_selection', models.IntegerField(blank='False', null='False')),
                ('bem_sample_selection', models.IntegerField(blank='False', null='False')),
                ('require_ontology_attributes_prior_count', models.IntegerField(blank='False', null='False')),
                ('converted_ontology_count', models.IntegerField(blank='False', null='False')),
                ('require_ontology_attributes_post_count', models.IntegerField(blank='False', null='False')),
                ('slots_backfilled_count', models.IntegerField(blank='False', null='False')),
                ('bem_publish_comment', models.CharField(blank='False', max_length=50, null='False')),
            ],
        ),
    ]
