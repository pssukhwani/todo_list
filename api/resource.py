from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from core.models import Task
from tastypie import fields
from tastypie.api import Api


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        list_allowed_methods = ['get', 'put', 'post', 'delete']

    def determine_format(self, request):
        return "application/json"


class TaskResource(ModelResource):
    user = fields.ForeignKey(UserResource, attribute='user')
    sub_task = fields.ForeignKey('self', attribute='sub_task', null=True)

    class Meta:
        queryset = Task.objects.all()
        resource_name = 'task'
        list_allowed_methods = ['get', 'put', 'post', 'delete']

    def determine_format(self, request):
        return "application/json"
