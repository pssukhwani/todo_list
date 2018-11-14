import json

from django.conf.urls import url
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from tastypie.resources import ModelResource

from core.models import Task
from tastypie import fields
from datetime import datetime


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
        list_allowed_methods = ['post']
        filtering = {'title': ALL}
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def determine_format(self, request):
        return "application/json"

    def prepend_urls(self):
        return [
            url(r"^task-create", self.wrap_view('task_create'), name="api_task"),
            url(r"^task-update", self.wrap_view('task_update'), name="api_task_update"),
        ]

    def get_object_list(self, request):
        task = super(TaskResource, self).get_object_list(request)
        if request.POST.get("delete"):
            return task.filter(id=request.POST.get("delete"), user=request.user, is_active=True)
        return task.filter(title=request.POST.get("title"), user=request.user, is_active=True)

    def obj_create(self, bundle, request=None, **kwargs):
        date_time = datetime.strptime(bundle.data.get("datetime"), "%d/%m/%Y %H:%M:%S")
        task = Task.objects.create(user=request.user, title=bundle.data.get("title"),
                                   description=bundle.data.get("description"), due_date=date_time,
                                   set_alert=bundle.data.get("set_alert"))
        bundle.obj = task
        bundle.obj.save()
        try:
            task_id = int(bundle.data.get("sub_task"))
        except:
            task_id = None
        if task_id:
            task_obj = Task.objects.get(id=task_id)
            try:
                bundle.obj.sub_task.add(task_obj)
                bundle.data.task_type = "child"
                bundle.data.save()
            except:
                pass
        return bundle

    def task_create(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        task_resource = TaskResource()
        bundle = task_resource.build_bundle(data=request.POST, request=request)
        task_query_set = task_resource.get_object_list(request)
        if task_query_set:
            return self.create_response(request, {
                'success': False,
                'reason': 'Title Already Exist',
            }, HttpBadRequest)
        self.obj_create(bundle, request)
        return self.create_response(request, {
                'success': True,
                'reason': 'Successfully added new task',
            })

    def task_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        task_resource = TaskResource()
        task_query_set = task_resource.get_object_list(request)
        if task_query_set:
            task_obj = task_query_set[0]
            task_obj.is_active = False
            task_obj.save()
            task_obj.sub_task.all().update(is_active=False)
            return self.create_response(request, {
                'success': True,
                'reason': 'Successfully Deleted task',
            })
        return self.create_response(request, {
            'success': False,
            'reason': "Couldn't find the task. Please refresh page and try again",
        })
