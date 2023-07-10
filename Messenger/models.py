from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import m2m_changed


def friends_changed(sender, **kwargs):
    if kwargs['action'] == 'pre_remove':
        companion = Users.objects.get(id__in=kwargs['pk_set']).user
        instance = kwargs['instance'].user
        Private_Log.objects.filter(From_User__in=[instance, companion], To_User__in=[instance, companion]).delete()
    

class Users(models.Model):
    """ Пользователи """
    user = models.OneToOneField(User, verbose_name="user", on_delete=models.CASCADE)
    Photo = models.ImageField("Photo", upload_to="photos/", blank=True)
    Friends = models.ManyToManyField("self", verbose_name="friends", blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.user.username

    def get_photo_url(self):
        if self.Photo:
            return self.Photo.url
        else:
            return settings.MEDIA_URL + 'photos/default.png'


m2m_changed.connect(friends_changed, sender=Users.Friends.through)


class Private_Log(models.Model):
    """ Логи сообщений """
    From_User = models.ForeignKey(User, verbose_name="From_User", related_name="From_User", on_delete=models.CASCADE)
    To_User = models.ForeignKey(User, verbose_name="To_User", related_name="To_User", on_delete=models.CASCADE)
    Message = models.TextField("Message", max_length=250)
    Date_Time = models.DateTimeField("Date_Time", auto_now_add=True)
    Status = models.BooleanField("Read_Status", default="False")

    class Meta:
        verbose_name = "Private Log"
        verbose_name_plural = "Private Logs"