from django.shortcuts import render
from datetime import datetime, timedelta

from core.models import Task


def home_page(request):
    data = {"api_name": "todo"}
    if request.user.is_authenticated:
        filter_list = ["today", "this_week", "next_week", "over_due"]
        filter_by = request.GET.get("filter_by_due_date")
        today = datetime.today().date()
        start_day = today - timedelta(days=today.weekday())
        end_day = start_day + timedelta(days=6)
        task = Task.objects.filter(user=request.user, is_active=True)
        if request.GET.get("search"):
            task = task.filter(title__icontains=request.GET.get("search"))
            data["search"] = request.GET.get("search")
        if filter_by in filter_list:
            if filter_by == 'over_due':
                task = task.filter(due_date__lt=today)
            if filter_by == 'today':
                task = task.filter(due_date=today)
            if filter_by == 'this_week':
                task = task.filter(due_date__gte=start_day, due_date__lte=end_day)
            if filter_by == 'next_week':
                task = task.filter(due_date__gt=end_day, due_date__lte=end_day + timedelta(days=7))
        data.update({"task": task.order_by("due_date"), "filter_by": filter_by})
        return render(request, "task.html", data)
    return render(request, "login_registration.html", data)
