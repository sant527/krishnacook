# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-16 18:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20170516_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='mass_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='pieces_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='volume_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='recipeposition',
            name='mass_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='recipeposition',
            name='pieces_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='recipeposition',
            name='volume_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
    ]