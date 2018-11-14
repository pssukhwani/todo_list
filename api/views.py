from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from core.models import Task


def home_page(request):
    data = {"api_name": "todo"}
    if request.user.is_authenticated:
        task = Task.objects.filter(user=request.user, is_active=True).order_by("due_date")
        data["task"] = task
        return render(request, "task.html", data)
    return render(request, "login_registration.html", data)
