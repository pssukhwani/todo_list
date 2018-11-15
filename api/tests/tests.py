# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from requests import get
from django.conf import settings


class TestMyView(object):
    url_list = ["api_login", "api_logout", "api_task", "api_task_update"]
    if settings.DEBUG:
        host_name = "https://pradeepsukhwani.pythonanywhere.com/"
    else:
        host_name = "http://localhost:8000"

    def test_result_finished(self):
        for url in self.url_list:
            response = get(self.host_name + reverse(url, kwargs={"api_name": "todo"}))
            assert response.status_code == 405 or response.status_code == 401
