from django.urls import path

from core import views

app_name = 'core'

urlpatterns = [
    path('profile/', views.settings, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
]
