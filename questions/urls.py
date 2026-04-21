from django.urls import path

from questions import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
]
