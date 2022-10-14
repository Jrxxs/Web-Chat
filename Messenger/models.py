from statistics import mode
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Users(models.Model):
    """ Пользователи """
    user = models.OneToOneField(User, verbose_name="user", on_delete=models.CASCADE)
    Photo = models.ImageField("Photo", upload_to="photos/", blank=True)
    Friends = models.ManyToManyField("self", verbose_name="friends", blank=True)

    def __str__(self):
        return self.user.username

    def get_photo_url(self):
        if self.Photo:
            return self.Photo.url
        else:
            return settings.MEDIA_URL + 'photos/default.png'

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Private_Log(models.Model):
    """ Логи сообщений """
    From_User = models.ForeignKey(User, verbose_name="From_User", related_name="From_User", on_delete=models.CASCADE)
    To_User = models.ForeignKey(User, verbose_name="To User", related_name="To_User", on_delete=models.CASCADE)
    Message = models.TextField("Message", max_length=250)
    Date_Time = models.DateTimeField("Date_Time", auto_now_add=True)

    # def __str__(self):
    #     return self.Message
    def last_20_messages(self):
        return Private_Log.objects.order_by('-Date_Time').all()[:20]

    class Meta:
        verbose_name = "Private Log"
        verbose_name_plural = "Private Logs"


class Chats(models.Model):
    """ Чаты """
    Name = models.CharField("ChatName", max_length=50)
    Admin = models.ForeignKey(User, verbose_name="Admin", on_delete=models.SET_NULL, null=True)
    UserS = models.ManyToManyField(User, verbose_name="Users", related_name="Chat_Users")

    def __str__(self):
        return self.Name

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"


class ChatsLog(models.Model):
    """ Логи чатов """
    Chat_Name = models.ForeignKey(Chats, verbose_name="Chat", on_delete=models.CASCADE)
    Message = models.TextField("Message", max_length=250)
    User_Name = models.CharField("User_Name", max_length=20)
    Date_Time = models.DateTimeField("Date_Time", auto_now_add=True)

    def __str__(self):
        return self.Chat_Name

    class Meta:
        verbose_name = "Chat Log"
        verbose_name_plural = "Chats Logs"
