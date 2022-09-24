from django.contrib import admin
from .models import Users, Private_Log, Chats, ChatsLog

admin.site.register(Users)
admin.site.register(Private_Log)
admin.site.register(Chats)
admin.site.register(ChatsLog)
