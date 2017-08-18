# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-16 04:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('single_measurements', '0001_initial'),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='primary_quantity',
        ),
        migrations.RemoveField(
            model_name='recipeposition',
            name='munit',
        ),
        migrations.RemoveField(
            model_name='recipeposition',
            name='quantity',
        ),
        migrations.AddField(
            model_name='recipe',
            name='mass_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='mass_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipe_singlemeasurement_mass_unit', to='single_measurements.SingleMeasurements'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='pieces_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='pieces_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipe_singlemeasurement_pieces_unit', to='single_measurements.SingleMeasurements'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='volume_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='volume_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipe_singlemeasurement_volume_unit', to='single_measurements.SingleMeasurements'),
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='cooking_notes',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='mass_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='mass_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipepoisition_singlemeasurement_mass_unit', to='single_measurements.SingleMeasurements'),
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='pieces_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='pieces_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipepoisition_singlemeasurement_pieces_unit', to='single_measurements.SingleMeasurements'),
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='primary_unit',
            field=models.CharField(choices=[('kg', 'Mass'), ('ltr', 'Volume'), ('pcs', 'Pieces')], default='kg', max_length=10),
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='volume_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='recipeposition',
            name='volume_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipepoisition_singlemeasurement_volume_unit', to='single_measurements.SingleMeasurements'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='primary_unit',
            field=models.CharField(choices=[('kg', 'Mass'), ('ltr', 'Volume'), ('pcs', 'Pieces')], default='kg', max_length=10),
        ),
    ]