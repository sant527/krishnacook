# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-18 18:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('single_measurements', '0003_auto_20170516_0736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singlemeasurements',
            name='quantity',
            field=models.DecimalField(decimal_places=10, default=1, max_digits=19),
            preserve_default=False,
        ),
    ]
