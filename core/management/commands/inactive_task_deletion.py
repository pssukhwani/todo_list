# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from core.models import Task
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Deleting if user has inactive tasks from almost a month.'

    def handle(self, **options):
        current_date_time = datetime.today()
        tasks = Task.objects.filter(is_active=False)
        for count, task_object in enumerate(tasks):
            get_reset_date = task_object.modified.date() + timedelta(days=30)
            if current_date_time >= get_reset_date:
                task_object.delete()
                print "Count:{count_number} - Task with {id} is deleted".format(id=task_object.id, count_number=count)
        print "No task are inactive"
