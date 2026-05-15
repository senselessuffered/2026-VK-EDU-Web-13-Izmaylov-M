from django import forms

from .models import Answer, Question, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'text': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 6}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Описание',
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author')
        super().__init__(*args, **kwargs)

    def clean_tags(self):
        raw_tags = self.cleaned_data['tags']
        tags = [tag.strip().lower() for tag in raw_tags.split(',') if tag.strip()]
        if len(tags) > 5:
            raise forms.ValidationError('Можно указать не больше 5 тегов.')
        return tags

    def save(self, commit=True):
        question = super().save(commit=False)
        question.author = self.author
        if commit:
            question.save()
            for tag_name in self.cleaned_data['tags']:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
                tag.questions_count = tag.questions.count()
                tag.save(update_fields=['questions_count'])
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 5}),
        }
        labels = {
            'text': 'Ваш ответ',
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author')
        self.question = kwargs.pop('question')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self.author
        answer.question = self.question
        if commit:
            answer.save()
            self.question.answers_count = self.question.answers.count()
            self.question.save(update_fields=['answers_count'])
        return answer
