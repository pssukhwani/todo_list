# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-15 13:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_task_task_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([]),
        ),
    ]
