from rest_framework import serializers
from .models import Users, User, Private_Log
from django.conf import settings

class UserCheckSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

class UsersSerializerAll(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UsersSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Users
        fields = ['id', 'get_photo_url', 'user']


class MessagesPageUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'get_photo_url']


class MessagesPageUserSerializer(serializers.ModelSerializer):
    users = MessagesPageUsersSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'users']


class LogSerializer(serializers.ModelSerializer):
    Date_Time = serializers.DateTimeField(format='%d/%m/%y %H:%M')

    class Meta:
        model = Private_Log
        fields = '__all__'

class UpdateLogSerializer(serializers.ModelSerializer):
    Date_Time = serializers.DateTimeField(format='%d/%m/%y %H:%M')
    From_User = UserSerializer()
    To_User = UserSerializer()

    class Meta:
        model = Private_Log
        fields = '__all__'

class PhotoSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.Photo.delete(False)
        return super().update(instance, validated_data)

    class Meta:
        model = Users
        fields = ['Photo']

class SettingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    new_password = serializers.CharField(required=False, write_only=True)
    confirm = serializers.CharField(required=False, write_only=True)
    users = PhotoSerializer()

    class Meta:
        model = User
        fields = ['username', 'password', 'new_password', 'confirm', 'users']
        
    def update(self, instance, validated_data):
        if bool(validated_data.get("username")) and validated_data.get("username") != instance.username:
            instance.username = validated_data.get("username")
            instance.save()
        if bool(validated_data.get("password")) and instance.check_password(validated_data.get("password")):
            if bool(validated_data.get("new_password")) and validated_data.get("new_password") == validated_data.get("confirm"):
                instance.set_password(str(validated_data['new_password']))
                instance.save()
        if bool(validated_data.get("users")):
            Photo = PhotoSerializer(instance.users, data=validated_data.pop('users'))
            Photo.is_valid(raise_exception=True)
            Photo.save()
        return instance