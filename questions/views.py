from django.shortcuts import render
from django.core.paginator import Paginator

# Create your views here.

questions = []
for i in range(1,50):
  questions.append({
    'title': 'title ' + str(i),
    'id': i,
    'text': 'text' + str(i),
    'tags': ['python', 'django'] if i % 2 == 0 else ['html', 'css']
  })

def pagination(request, questions):
    page_number = int(request.GET.get('page', 1))
    page = Paginator(questions, 10)
    page_obj = page.page(page_number)
    return page_obj

def ask(request):
    return render(request, 'ask.html')

def index(request):
    page_obj = pagination(request, questions)
    return render(request, 'index.html', context={'questions': page_obj.object_list, 'page_obj': page_obj})

def hot(request):
    page_obj = pagination(request, questions[::-1])
    return render(request, 'hot.html', context={'questions': page_obj.object_list, 'page_obj': page_obj})

def question(request, question_id):
    question = None
    for q in questions:
        if q['id'] == question_id:
            question = q
            break
    return render(request, 'question.html', context={'question': question})

def tag(request, tag_name):
    questions_with_tag = [q for q in questions if tag_name in q['tags']]
    page_obj = pagination(request, questions_with_tag)
    return render(request, 'index.html', context={'tag_name': tag_name, 'questions': page_obj.object_list, 'page_obj': page_obj})