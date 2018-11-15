# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import pytest
from django.urls import reverse
from requests import get
from core.models import Task


class TestMyView(object):
    url_list = ["api_login", "api_logout", "api_task", "api_task_update"]

    def test_result_finished(self, rf):
        for url in self.url_list:
            response = get(reverse(url))
            assert response.status_code == 200
