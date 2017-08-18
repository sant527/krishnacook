# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-24 17:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20170524_1309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='sequence_number',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
    ]
