import json

from django.conf.urls import url
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.db.models import Q
from tastypie.constants import ALL
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from core.models import Task
from tastypie import fields


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        list_allowed_methods = ['post']

    def determine_format(self, request):
        return "application/json"

    def get_object_list(self, request):
        users = super(UserResource, self).get_object_list(request)
        return users.filter(Q(username=request.POST.get("username")) | Q(email=request.POST.get("email")))

    def prepend_urls(self):
        return [
            url(r"^login", self.wrap_view('login'), name="api_login"),
            url(r'^logout', self.wrap_view('logout'), name='api_logout'),
            url(r'^signup', self.wrap_view('signup'), name='api_signup'),
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
                    'success': True
                })
            return self.create_response(request, {
                'success': False,
                'reason': 'disabled',
            }, HttpForbidden)
        return self.create_response(request, {
            'success': False,
            'reason': 'Incorrect username and password',
        }, HttpUnauthorized)

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False}, HttpUnauthorized)

    def obj_create(self, bundle, request=None, **kwargs):
        username = bundle.data['username']
        password = bundle.data['password']
        email = bundle.data['email']
        user = User.objects.create_user(username=username, password=password, email=email)
        return user

    def signup(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.serialize(request, request.POST, format=self.determine_format(request))
        data = json.loads(data)
        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)
        confirm_password = data.get('confirm-password', None)
        user_object = self.get_object_list(request)
        if user_object:
            return self.create_response(request, {
                'success': False,
                'reason': 'User already exist',
            }, HttpUnauthorized)

        if password != confirm_password:
            return self.create_response(request, {
                'success': False,
                'reason': 'Password do not match',
            }, HttpUnauthorized)

        user = self.obj_create(data, request)

        if user:
            login(request, user)
            return self.create_response(request, {
                'success': True
            })


class TaskResource(ModelResource):
    user = fields.ForeignKey(UserResource, attribute='user')
    sub_task = fields.ForeignKey('self', attribute='sub_task', null=True)

    class Meta:
        queryset = Task.objects.all()
        resource_name = 'task'
        list_allowed_methods = ['get', 'put', 'post', 'delete']
        filtering = {'title': ALL}

    def determine_format(self, request):
        return "application/json"
