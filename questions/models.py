from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class QuestionManager(models.Manager):
    def with_details(self):
        return (
            self.get_queryset()
            .select_related('author', 'author__profile')
            .prefetch_related('tags')
        )

    def new(self):
        return self.with_details().order_by('-created_at')

    def best(self):
        return self.with_details().order_by('-rating', '-created_at')

    def by_tag(self, tag_name):
        return self.with_details().filter(tags__name=tag_name).order_by('-created_at')


class AnswerManager(models.Manager):
    def with_details(self):
        return self.get_queryset().select_related('author', 'author__profile')

    def for_question(self, question):
        return self.with_details().filter(question=question).order_by('-rating', 'created_at')


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='название')
    questions_count = models.PositiveIntegerField(
        default=0,
        verbose_name='количество вопросов',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='автор',
    )
    title = models.CharField(max_length=255, verbose_name='заголовок')
    text = models.TextField(verbose_name='текст')
    tags = models.ManyToManyField(
        Tag,
        related_name='questions',
        blank=True,
        verbose_name='теги',
    )
    rating = models.IntegerField(default=0, db_index=True, verbose_name='рейтинг')
    answers_count = models.PositiveIntegerField(
        default=0,
        verbose_name='количество ответов',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='создан',
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='обновлен')

    objects = QuestionManager()

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('questions:question', kwargs={'question_id': self.pk})


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='вопрос',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='автор',
    )
    text = models.TextField(verbose_name='текст')
    is_correct = models.BooleanField(default=False, verbose_name='правильный ответ')
    rating = models.IntegerField(default=0, db_index=True, verbose_name='рейтинг')
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='создан',
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='обновлен')

    objects = AnswerManager()

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'
        ordering = ['-rating', 'created_at']

    def __str__(self):
        return f'Ответ #{self.pk} на вопрос #{self.question_id}'


class QuestionLike(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='вопрос',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name='пользователь',
    )
    value = models.SmallIntegerField(default=1, verbose_name='оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создана')

    class Meta:
        verbose_name = 'лайк вопроса'
        verbose_name_plural = 'лайки вопросов'
        unique_together = ('question', 'user')

    def __str__(self):
        return f'{self.user_id} -> question {self.question_id}'


class AnswerLike(models.Model):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='ответ',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name='пользователь',
    )
    value = models.SmallIntegerField(default=1, verbose_name='оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создана')

    class Meta:
        verbose_name = 'лайк ответа'
        verbose_name_plural = 'лайки ответов'
        unique_together = ('answer', 'user')

    def __str__(self):
        return f'{self.user_id} -> answer {self.answer_id}'
