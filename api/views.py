from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from core.models import Task


def home_page(request):
    data = {"api_name": "todo"}
    if request.user.is_authenticated:
        task = Task.objects.filter(user=request.user, is_active=True)
        if request.GET.get("search"):
            task = task.filter(title__icontains=request.GET.get("search"))
            data["success"] = True
        data["task"] = task
        return render(request, "task.html", data)
    return render(request, "login_registration.html", data)
