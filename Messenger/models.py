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
    Status = models.BooleanField("Read_Status", default="False")

    # def __str__(self):
    #     return self.Message
    def last_20_messages(self):
        x = Private_Log.objects.get(Read_Status=False)
        print(x)
        return Private_Log.objects.order_by('-Date_Time').all()[:20]

    class Meta:
        verbose_name = "Private Log"
        verbose_name_plural = "Private Logs"