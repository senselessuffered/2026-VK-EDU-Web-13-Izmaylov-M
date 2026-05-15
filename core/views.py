from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, ProfileForm, SignupForm
from .models import Profile


def get_safe_next_url(request):
    next_url = request.POST.get('next') or request.GET.get('next') or ''
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return ''


def login_view(request):
    form = LoginForm(request.POST or None)
    next_url = get_safe_next_url(request)
    if request.method == 'POST' and form.is_valid():
        login(request, form.cleaned_data['user'])
        return redirect(next_url or reverse('questions:index'))
    return render(request, 'login.html', {'form': form, 'next': next_url})


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('questions:index')
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    next_url = request.META.get('HTTP_REFERER') or reverse('questions:index')
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = reverse('questions:index')
    logout(request)
    return redirect(next_url)


@login_required(login_url='core:login')
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
        profile=profile_obj,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('core:profile')
    return render(request, 'profile.html', {'form': form})
