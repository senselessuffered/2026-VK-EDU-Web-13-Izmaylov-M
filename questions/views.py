from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AnswerForm, CorrectAnswerForm, QuestionForm, VoteForm
from .models import Answer, AnswerLike, Question, QuestionLike, Tag
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

    user_question_vote = 0
    if request.user.is_authenticated:
        like = QuestionLike.objects.filter(question=question, user=request.user).first()
        if like:
            user_question_vote = like.value
        answer_votes = {
            like.answer_id: like.value
            for like in AnswerLike.objects.filter(
                answer_id__in=[a.id for a in page_obj.object_list],
                user=request.user,
            )
        }
        for answer in page_obj.object_list:
            answer.user_vote = answer_votes.get(answer.id, 0)
    else:
        for answer in page_obj.object_list:
            answer.user_vote = 0

    return render(request, 'question.html', context={
        'question': question,
        'answers': page_obj.object_list,
        'page_obj': page_obj,
        'answer_form': answer_form,
        'user_question_vote': user_question_vote,
        'is_question_author': request.user.is_authenticated and request.user.id == question.author_id,
    })


def tag(request, tag_name):
    tag_exists = Tag.objects.filter(name=tag_name).exists()
    page_obj = paginate(request, Question.objects.by_tag(tag_name))
    return render(request, 'index.html', context={'tag_name': tag_name, 'tag_exists': tag_exists, 'questions': page_obj.object_list, 'page_obj': page_obj})


@require_POST
def vote_question(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=401)

    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid', 'details': form.errors}, status=400)

    question = get_object_or_404(Question, pk=form.cleaned_data['target_id'])
    value = form.cleaned_data['value']

    like, created = QuestionLike.objects.get_or_create(
        question=question, user=request.user,
        defaults={'value': value},
    )

    if created:
        delta = value
    elif like.value != value:
        delta = value - like.value
        like.value = value
        like.save(update_fields=['value'])
    else:
        delta = 0

    if delta:
        Question.objects.filter(pk=question.pk).update(rating=F('rating') + delta)
        question.refresh_from_db(fields=['rating'])

    return JsonResponse({'rating': question.rating, 'user_value': value})


@require_POST
def vote_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=401)

    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid', 'details': form.errors}, status=400)

    answer = get_object_or_404(Answer, pk=form.cleaned_data['target_id'])
    value = form.cleaned_data['value']

    like, created = AnswerLike.objects.get_or_create(
        answer=answer, user=request.user,
        defaults={'value': value},
    )

    if created:
        delta = value
    elif like.value != value:
        delta = value - like.value
        like.value = value
        like.save(update_fields=['value'])
    else:
        delta = 0

    if delta:
        Answer.objects.filter(pk=answer.pk).update(rating=F('rating') + delta)
        answer.refresh_from_db(fields=['rating'])

    return JsonResponse({'rating': answer.rating, 'user_value': value})


@require_POST
def mark_correct(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=401)

    form = CorrectAnswerForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid', 'details': form.errors}, status=400)

    answer = get_object_or_404(Answer.objects.select_related('question'), pk=form.cleaned_data['answer_id'])

    if answer.question.author_id != request.user.id:
        return JsonResponse({'error': 'forbidden'}, status=403)

    answer.is_correct = not answer.is_correct
    answer.save(update_fields=['is_correct'])

    return JsonResponse({'is_correct': answer.is_correct})
