# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-15 13:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('typeofingredient', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('munit', models.CharField(choices=[('kg', 'Kilogram'), ('ltr', 'Liter'), ('pcs', 'Pieces')], default='kg', max_length=10)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=19)),
                ('density', models.DecimalField(blank=True, decimal_places=2, help_text='Density is always Kg/lt or kg/piece. You can leave it empty unless you have to use the ingredient in volumes like cups, tubs or liters.', max_digits=19, null=True, verbose_name='Density')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('typeofingredient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='typeof_ingredient', to='typeofingredient.TypeOfIngredient')),
            ],
            options={
                'ordering': ['-updated', '-timestamp'],
            },
        ),
    ]
