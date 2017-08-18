# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-16 18:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20170516_0736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='primary_unit',
            field=models.CharField(blank=True, choices=[('kg', 'Mass'), ('ltr', 'Volume'), ('pcs', 'Pieces')], default='ltr', help_text='Nothing significant for calculation. Only useful for Display. Eg: we enter Chapatis recipe Volume/Mass/Pieces Units, which are below this as 1 tub == 50 kg == 400 pieces. If we choose Volume, we will show the recipe name as: Chaptti for 1 tub, If we choose Mass then: Chappati for 50 kg, If we choose Pieces then: Chappati for 400 pices.', max_length=10, null=True, verbose_name='Preferred Display Units'),
        ),
        migrations.AlterField(
            model_name='recipeposition',
            name='name',
            field=models.CharField(blank=True, help_text='If left blank will be same as Ingredient name Eg: Tomato pulp', max_length=200),
        ),
        migrations.AlterField(
            model_name='recipeposition',
            name='primary_unit',
            field=models.CharField(blank=True, choices=[('kg', 'Mass'), ('ltr', 'Volume'), ('pcs', 'Pieces')], default='kg', help_text='Nothing significant for calculation. Only useful for Display. Eg: we enter Nimbu ingredients Volume/Mass/Pieces Units, which are below this as 1 mug == 0.7 kg == 100 pieces. If we choose Volume, we will show the ingredient name as: Nimbu - 1 mug, If we choose Mass then: Nimbu - 0.7 kg, If we choose Pieces then: Nimbu - 100 pieces.', max_length=10, null=True, verbose_name='Preferred Display Units'),
        ),
    ]