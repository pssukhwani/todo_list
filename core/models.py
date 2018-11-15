# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django_extensions.db.models import TimeStampedModel, models
from django_extensions.db.fields import AutoSlugField


STATE_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
)


class Task(TimeStampedModel):
    is_active = models.BooleanField("Is Active", default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=255, db_index=True)
    description = models.TextField("Description", blank=True, null=True)
    state = models.CharField("State", choices=STATE_CHOICES, max_length=10, default='pending')
    due_date = models.DateTimeField("Due Date", blank=True, null=True)
    slug = AutoSlugField(populate_from='title')
    sub_task = models.ManyToManyField("self", blank=True, null=True, help_text="This is for sub task")
    set_alert = models.PositiveSmallIntegerField(default=0, blank=True, null=True,
                                                 help_text="This is used for alert message. If you want to trigger "
                                                           "alert before due date then only set this.")

    class Meta:
        ordering = ("due_date",)

    def __str__(self):
        return u"{title}".format(title=self.slug)
