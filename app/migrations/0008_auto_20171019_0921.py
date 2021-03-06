# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-19 07:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20171013_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='positivebalance',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Offer'),
        ),
        migrations.AddField(
            model_name='positivebalance',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Transaction'),
        ),
        migrations.AddField(
            model_name='positivebalance',
            name='type',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='offer',
            name='address',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Adresa'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='address_type',
            field=models.IntegerField(choices=[(1, 'Kućna adresa'), (2, 'Druga adresa')], default=1, help_text='Gdje se može preuzeti vaša roba/usluga?', verbose_name='Adresa preuzimanja'),
        ),
    ]
