from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.templatetags.static import static
from django.utils import timezone

from .models import Answer, Question, QuestionLike, Tag

POPULAR_TAGS_LIMIT = 10
POPULAR_TAGS_PERIOD_DAYS = 90

BEST_MEMBERS_LIMIT = 10
BEST_MEMBERS_PERIOD_DAYS = 7


def paginate(request, objects, per_page=10):
    paginator = Paginator(objects, per_page)
    return paginator.get_page(request.GET.get('page'))


def annotate_user_votes(questions, user):
    if user.is_authenticated:
        votes = dict(
            QuestionLike.objects
            .filter(question__in=questions, user=user)
            .values_list('question_id', 'value')
        )
    else:
        votes = {}
    for question in questions:
        question.user_vote = votes.get(question.id, 0)
    return questions


def compute_popular_tags():
    since = timezone.now() - timedelta(days=POPULAR_TAGS_PERIOD_DAYS)
    tags = (
        Tag.objects
        .annotate(recent_questions=Count('questions', filter=Q(questions__created_at__gte=since)))
        .filter(recent_questions__gt=0)
        .order_by('-recent_questions', 'name')[:POPULAR_TAGS_LIMIT]
    )
    return [{'name': tag.name, 'count': tag.recent_questions} for tag in tags]


def compute_best_members():
    since = timezone.now() - timedelta(days=BEST_MEMBERS_PERIOD_DAYS)

    scores = defaultdict(int)
    for row in Question.objects.filter(created_at__gte=since).values('author').annotate(points=Sum('rating')):
        scores[row['author']] += row['points'] or 0
    for row in Answer.objects.filter(created_at__gte=since).values('author').annotate(points=Sum('rating')):
        scores[row['author']] += row['points'] or 0

    top = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:BEST_MEMBERS_LIMIT]

    users_by_id = {
        user.id: user
        for user in User.objects.filter(id__in=[uid for uid, _ in top]).select_related('profile')
    }

    members = []
    for user_id, points in top:
        user = users_by_id.get(user_id)
        if user is None:
            continue
        avatar = getattr(getattr(user, 'profile', None), 'avatar', None)
        members.append({
            'username': user.username,
            'points': points,
            'avatar_url': avatar.url if avatar else static('img/avatar-default.jpg'),
        })
    return members


def rebuild_popular_tags_cache():
    data = compute_popular_tags()
    cache.set(settings.CACHE_KEY_POPULAR_TAGS, data, settings.SIDEBAR_CACHE_TIMEOUT)
    return data


def rebuild_best_members_cache():
    data = compute_best_members()
    cache.set(settings.CACHE_KEY_BEST_MEMBERS, data, settings.SIDEBAR_CACHE_TIMEOUT)
    return data


def get_popular_tags():
    data = cache.get(settings.CACHE_KEY_POPULAR_TAGS)
    if data is None:
        data = rebuild_popular_tags_cache()
    return data


def get_best_members():
    data = cache.get(settings.CACHE_KEY_BEST_MEMBERS)
    if data is None:
        data = rebuild_best_members_cache()
    return data
