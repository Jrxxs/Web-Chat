# Generated by Django 4.1.7 on 2023-03-18 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger', '0007_private_log_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatslog',
            name='Chat_Name',
        ),
        migrations.DeleteModel(
            name='Chats',
        ),
        migrations.DeleteModel(
            name='ChatsLog',
        ),
    ]
