from django.conf.urls import url
from tastypie.api import Api

from resource import UserResource, TaskResource
from views import index


todo_api = Api(api_name='todo')
todo_api.register(UserResource())
todo_api.register(TaskResource())

urlpatterns = todo_api.urls

urlpatterns += [
    url(r'^index$', index, name='index'),
]
