import json

from django.conf.urls import url
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest, HttpNotModified
from tastypie.resources import ModelResource

from core.models import Task
from tastypie import fields
from datetime import datetime, timedelta


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
        elif request.GET.get("testing"):
            # Only For Testing Purpose
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
            url(r"^task-detail", self.wrap_view('task_details'), name="api_task_detail"),
        ]

    def get_object_list(self, request):
        task = super(TaskResource, self).get_object_list(request)
        # Only For Testing Purpose
        if request.POST.get("testing"):
            request.user = User.objects.all()[0]
        if request.POST.get("delete") or request.POST.get("checked") or request.POST.get("modalUpdate"):
            task_id = request.POST.get("delete") or request.POST.get("checked") or request.POST.get("id")
            return task.filter(id=task_id, user=request.user, is_active=True)
        return task.filter(title=request.POST.get("title"), user=request.user, is_active=True)

    def obj_update(self, bundle, request=None, **kwargs):
        task = Task.objects.get(id=bundle.data.get("id"))
        task.title = bundle.data.get("title")
        task.description = bundle.data.get("description")
        try:
            task.due_date = datetime.strptime(bundle.data.get("date"), "%d/%m/%Y %H:%M:%S")
        except ValueError:
            task.due_date = None
        task.set_alert = bundle.data.get("set_alert")
        task.save()
        bundle.obj = task
        bundle.obj.save()
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        # Only For Testing Purpose
        if request.POST.get("testing"):
            request.user = User.objects.all()[0]
        try:
            date_time = datetime.strptime(bundle.data.get("datetime"), "%d/%m/%Y %H:%M:%S")
        except ValueError:
            date_time = None
        task = Task.objects.create(user=request.user, title=bundle.data.get("title"),
                                   description=bundle.data.get("description"), due_date=date_time,
                                   set_alert=bundle.data.get("set_alert"))
        try:
            task_id = int(bundle.data.get("sub_task"))
        except:
            task_id = None
        if task_id:
            task_obj = Task.objects.get(id=task_id)
            try:
                task.sub_task.add(task_obj)
                task.save()
            except:
                pass
        bundle.obj = task
        bundle.obj.save()
        return bundle

    def get_bundle_data(self, request, resource):
        bundle = resource.build_bundle(data=request.POST, request=request)
        return bundle

    def task_create(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        task_resource = TaskResource()
        bundle = self.get_bundle_data(request, task_resource)
        self.obj_create(bundle, request)
        return self.create_response(request, {
                'success': True,
                'reason': 'Successfully added new task',
            })

    def task_details(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        task_query_set = Task.objects.filter(is_active=True)
        task_list_ids = []
        for task in task_query_set:
            if task.due_date:
                task_with_alert = task.due_date.replace(tzinfo=None) - timedelta(hours=task.set_alert)
                if task_with_alert <= datetime.today():
                    task_list_ids.append(task.id)
        if task_list_ids:
            return self.create_response(request, {
                    'success': True,
                    'reason': 'New Notification',
                    'task': list(task_query_set.filter(id__in=task_list_ids).values())
                })
        return self.create_response(request, {
            'success': True,
            'reason': 'No New Notification',
        })

    def task_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        task_resource = TaskResource()
        task_query_set = task_resource.get_object_list(request)
        bundle = self.get_bundle_data(request, task_resource)
        if not task_query_set:
            return self.create_response(request, {
                'success': False,
                'reason': "Couldn't find the task. Please refresh page and try again",
            }, HttpBadRequest)
        task_obj = task_query_set[0]
        if request.POST.get("delete"):
            task_obj.is_active = False
            task_obj.save()
            task_obj.sub_task.all().update(is_active=False)
            return self.create_response(request, {
                'success': True,
                'reason': 'Successfully Deleted task',
            })
        elif request.POST.get("checked"):
            if request.POST.get("needCheck") == 'true':
                task_obj.state = 'completed'
                task_obj.sub_task.all().update(state='completed')
            else:
                task_obj.state = 'pending'
                task_obj.sub_task.all().update(state='pending')
            task_obj.save()
            return self.create_response(request, {
                'success': True,
                'reason': 'Successfully saved task preferences',
            })
        elif request.POST.get("title"):
            self.obj_update(bundle, request)
            return self.create_response(request, {
                'success': True,
                'reason': 'Successfully saved task preferences',
            })
        return self.create_response(request, {
            'success': False,
            'reason': "Couldn't find the task. Please refresh page and try again",
        }, HttpBadRequest)
