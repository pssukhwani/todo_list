import json

from django.conf.urls import url
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.resources import ModelResource

from core.models import Task
from tastypie import fields


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        list_allowed_methods = ['post']

    def determine_format(self, request):
        return "application/json"

    def prepend_urls(self):
        return [
            url(r"^login", self.wrap_view('login'), name="api_login"),
            url(r'^logout', self.wrap_view('logout'), name='api_logout'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.serialize(request, request.POST, format=self.determine_format(request))
        data = json.loads(data)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True,
                    'reason': "Successfully logged in"
                })
            return self.create_response(request, {
                'success': False,
                'reason': 'Account is disabled',
            }, HttpForbidden)
        return self.create_response(request, {
            'success': False,
            'reason': 'Incorrect username and password',
        }, HttpUnauthorized)

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return HttpResponseRedirect('/')
        else:
            return self.create_response(request, {'success': False}, HttpUnauthorized)


class TaskResource(ModelResource):
    user = fields.ForeignKey(UserResource, attribute='user')
    sub_task = fields.ForeignKey('self', attribute='sub_task', null=True)

    class Meta:
        queryset = Task.objects.all()
        resource_name = 'task'
        list_allowed_methods = ['get', 'post', 'delete']
        filtering = {'title': ALL}
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def determine_format(self, request):
        return "application/json"

    def prepend_urls(self):
        return [
            url(r"^task", self.wrap_view('task'), name="api_task"),
            url(r"^task-delete", self.wrap_view('task-update'), name="api_task_update"),
        ]

    def get_object_list(self, request):
        task = super(TaskResource, self).get_object_list(request)
        return task.filter(user=request.user)

    def task(self, request, **kwargs):
        pass

    def task_update(self, request, **kwargs):
        pass
