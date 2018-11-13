from django.conf.urls import url
from tastypie.api import Api

from api.views import home_page
from resource import UserResource, TaskResource


todo_api = Api(api_name='todo')
todo_api.register(UserResource())
todo_api.register(TaskResource())

urlpatterns = todo_api.urls

urlpatterns += [
    url(r'^$', home_page, name='home'),
]
