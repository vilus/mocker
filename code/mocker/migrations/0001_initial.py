# Generated by Django 2.2.3 on 2019-08-24 10:52

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('name', models.CharField(max_length=16, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Mock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='*', max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expired', models.DateTimeField(blank=True, null=True)),
                ('ttl', models.PositiveIntegerField(default=120)),
                ('is_exclusive', models.BooleanField(default=False)),
                ('host', models.CharField(default='*', max_length=120)),
                ('route', models.CharField(default='*', max_length=120)),
                ('method', models.CharField(default='*', max_length=120)),
                ('responses', django.contrib.postgres.fields.jsonb.JSONField()),
                ('response_type', models.CharField(choices=[('cycle', 'cycle'), ('sequence', 'sequence')], default='sequence', max_length=20)),
            ],
        ),
    ]
