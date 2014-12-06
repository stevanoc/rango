# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0005_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='views',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
