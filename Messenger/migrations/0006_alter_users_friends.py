# Generated by Django 4.1.2 on 2022-10-14 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger', '0005_users_friends'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='Friends',
            field=models.ManyToManyField(blank=True, to='Messenger.users', verbose_name='friends'),
        ),
    ]