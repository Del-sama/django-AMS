# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-23 09:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ams_app', '0006_auto_20171021_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('Lecturer', 'Lecturer'), ('Student', 'Student')], default='Lecturer', max_length=100),
        ),
    ]
