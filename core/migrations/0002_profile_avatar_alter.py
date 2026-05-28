import django.core.validators
from django.db import migrations, models

import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=core.models.avatar_upload_to,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
                    )
                ],
                verbose_name='аватар',
            ),
        ),
    ]
