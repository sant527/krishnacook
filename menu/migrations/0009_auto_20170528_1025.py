# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-28 10:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0008_auto_20170525_0409'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='menuposition',
            options={'ordering': ['-updated']},
        ),
    ]
