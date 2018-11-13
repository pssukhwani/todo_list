from django.shortcuts import render


def home_page(request):
    if request.user.is_authenticated:
        data = {"api_name": "todo"}
        return render(request, "task.html", data)
    data = {"api_name": "todo"}
    return render(request, "login_registration.html", data)
