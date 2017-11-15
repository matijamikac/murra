# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-04 08:57
from __future__ import unicode_literals

from django.db import migrations
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20170928_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_photo',
            field=stdimage.models.StdImageField(default='images/profile_photos/no_photo.png', help_text='Opcionalna profilna fotografija', upload_to='images/profile_photos', verbose_name='Fotografija'),
        ),
    ]
