# Generated by Django 4.1.2 on 2022-10-19 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recorder', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recording',
            name='duration',
            field=models.DurationField(blank=True, default=None, null=True),
        ),
    ]
