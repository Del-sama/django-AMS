# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-21 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ams_app', '0004_submission_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='matric_number',
            field=models.CharField(max_length=12, null=True, unique=True),
        ),
    ]
