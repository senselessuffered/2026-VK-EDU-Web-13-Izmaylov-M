from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.models import User

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if username and password and user is None:
            raise forms.ValidationError('Неверный логин или пароль.')
        cleaned_data['user'] = user
        return cleaned_data


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }
        labels = {
            'username': 'Логин',
            'email': 'Email',
        }

    def clean_password(self):
        password = self.cleaned_data['password']
        password_validation.validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(user=user)
        return user


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(label='Аватар', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))

    class Meta:
        model = User
        fields = ('email', 'username')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }
        labels = {
            'email': 'Email',
            'username': 'Логин',
        }

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile')
        super().__init__(*args, **kwargs)
        self.fields['avatar'].initial = self.profile.avatar

    def save(self, commit=True):
        user = super().save(commit=commit)
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            self.profile.avatar = avatar
            if commit:
                self.profile.save()
        return user
