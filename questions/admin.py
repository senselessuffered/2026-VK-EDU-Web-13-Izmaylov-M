from django.contrib import admin
from .models import Answer, AnswerLike, Question, QuestionLike, Tag

# Register your models here.

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ('author',)
    fields = ('author', 'text', 'is_correct', 'rating', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'rating', 'answers_count', 'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('created_at', 'tags')
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)
    inlines = (AnswerInline,)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'is_correct', 'rating', 'created_at')
    search_fields = ('text', 'author__username', 'question__title')
    list_filter = ('is_correct', 'created_at')
    raw_id_fields = ('question', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'questions_count')
    search_fields = ('name',)


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user', 'value', 'created_at')
    search_fields = ('question__title', 'user__username')
    list_filter = ('value', 'created_at')
    raw_id_fields = ('question', 'user')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer', 'user', 'value', 'created_at')
    search_fields = ('answer__text', 'user__username')
    list_filter = ('value', 'created_at')
    raw_id_fields = ('answer', 'user')
