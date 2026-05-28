from django.urls import path

from questions import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('search/', views.search, name='search'),
    path('ajax/vote-question/', views.vote_question, name='vote_question'),
    path('ajax/vote-answer/', views.vote_answer, name='vote_answer'),
    path('ajax/mark-correct/', views.mark_correct, name='mark_correct'),
]
