# Generated by Django 3.1.2 on 2020-10-09 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='profile',
            fields=[
                ('pid', models.AutoField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(blank='False', max_length=50, null='False')),
                ('user_role', models.CharField(blank='False', max_length=50, null='False')),
                ('special_role1', models.CharField(blank='False', max_length=50, null='False')),
                ('special_role2', models.CharField(blank='False', max_length=50, null='False')),
            ],
        ),
    ]