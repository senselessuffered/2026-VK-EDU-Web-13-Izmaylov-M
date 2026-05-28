from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.templatetags.static import static
from django.utils import timezone

from . import centrifugo
from .models import Answer


@shared_task
def refresh_popular_tags():
    from . import services
    return len(services.rebuild_popular_tags_cache())


@shared_task
def refresh_best_members():
    from . import services
    return len(services.rebuild_best_members_cache())


@shared_task
def publish_new_answer(answer_id):
    answer = (
        Answer.objects
        .select_related('author', 'author__profile', 'question')
        .filter(pk=answer_id)
        .first()
    )
    if answer is None:
        return None

    avatar = getattr(getattr(answer.author, 'profile', None), 'avatar', None)
    payload = {
        'answer_id': answer.id,
        'author_id': answer.author_id,
        'author_username': answer.author.username,
        'avatar_url': avatar.url if avatar else static('img/avatar-default.jpg'),
        'text': answer.text,
        'created_at': timezone.localtime(answer.created_at).strftime('%d.%m.%Y %H:%M'),
        'rating': answer.rating,
        'answers_count': answer.question.answers_count,
    }
    channel = centrifugo.channel_for_question(answer.question_id)
    centrifugo.publish(channel, payload)
    return channel


@shared_task
def send_new_answer_email(answer_id):
    answer = (
        Answer.objects
        .select_related('author', 'question', 'question__author')
        .filter(pk=answer_id)
        .first()
    )
    if answer is None:
        return None

    question = answer.question
    recipient = question.author.email
    if not recipient or answer.author_id == question.author_id:
        return None

    subject = f'Новый ответ на ваш вопрос «{question.title}»'
    message = (
        f'Пользователь {answer.author.username} ответил на ваш вопрос «{question.title}».\n\n'
        f'{answer.text}\n\n'
        f'Открыть вопрос: {question.get_absolute_url()}'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    return recipient
