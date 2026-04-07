from django.shortcuts import render

# Create your views here.

def settings(request):
    return render(request, 'settings.html', context={'user': 'John Doe', 'email': 'john.doe@example.com', 'password': 'password123'})

def signup(request):
    return render(request, 'core/templates/signup.html')

def login_view(request):
    return render(request, 'login.html')