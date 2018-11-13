# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from core.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'user', 'state', 'task_type',)
    exclude = ('task_type',)


admin.site.register(Task, TaskAdmin)
