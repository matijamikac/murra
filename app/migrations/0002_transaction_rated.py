# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-28 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='rated',
            field=models.BooleanField(default=False),
        ),
    ]
