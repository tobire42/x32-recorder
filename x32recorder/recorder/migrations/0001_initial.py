# Generated by Django 4.1.2 on 2022-10-18 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('filename', models.CharField(max_length=256)),
                ('channel_count', models.IntegerField()),
                ('duration', models.DurationField()),
                ('state', models.IntegerField(default=0)),
            ],
        ),
    ]
