from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnswerForm, QuestionForm
from .models import Answer, Question, Tag
from .services import paginate

@login_required(login_url='core:login')
def ask(request):
    form = QuestionForm(request.POST or None, author=request.user)
    if request.method == 'POST' and form.is_valid():
        question = form.save()
        return redirect(question.get_absolute_url())
    return render(request, 'ask.html', {'form': form})

def index(request):
    page_obj = paginate(request, Question.objects.new())
    return render(request, 'index.html', context={'questions': page_obj.object_list, 'page_obj': page_obj})

def hot(request):
    page_obj = paginate(request, Question.objects.best())
    return render(request, 'hot.html', context={'questions': page_obj.object_list, 'page_obj': page_obj})

def question(request, question_id):
    question = get_object_or_404(Question.objects.with_details(), pk=question_id)
    answer_form = None
    if request.user.is_authenticated:
        answer_form = AnswerForm(request.POST or None, author=request.user, question=question)
        if request.method == 'POST' and answer_form.is_valid():
            answer = answer_form.save()
            page = Answer.objects.for_question(question).filter(rating__gt=answer.rating).count() // 4 + 1
            return redirect(f'{question.get_absolute_url()}?page={page}#answer-{answer.id}')
    page_obj = paginate(request, Answer.objects.for_question(question), per_page=4)
    return render(request, 'question.html', context={'question': question, 'answers': page_obj.object_list, 'page_obj': page_obj, 'answer_form': answer_form})

def tag(request, tag_name):
    tag_exists = Tag.objects.filter(name=tag_name).exists()
    page_obj = paginate(request, Question.objects.by_tag(tag_name))
    return render(request, 'index.html', context={'tag_name': tag_name, 'tag_exists': tag_exists, 'questions': page_obj.object_list, 'page_obj': page_obj})
