# Generated by Django 4.1 on 2022-09-20 15:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Messenger', '0002_remove_users_login_remove_users_password_users_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
    ]
