# Generated by Django 4.1.2 on 2023-01-25 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger', '0006_alter_users_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='private_log',
            name='Status',
            field=models.BooleanField(default='False', verbose_name='Read_Status'),
        ),
    ]