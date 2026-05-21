import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


def avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'avatars/{uuid.uuid4().hex}{ext}'


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='пользователь',
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_to,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])],
        verbose_name='аватар',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='обновлен')

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return self.user.username
