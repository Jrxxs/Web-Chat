from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, HTMLFormRenderer
from rest_framework.views import APIView
from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
import re

from .models import Users, Private_Log, User
from .forms import LoginUserForm, RegistrationForm
from . import Serializers


class LoginPage(View):
    """ Страница авторизации """
    temlate_name = 'registration/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home', request.user.id)
        users = User.objects.filter(is_staff=False)
        context = {
            'form': LoginUserForm
        }
        return render(request, self.temlate_name, {'UsErS': users, 'context': context})
    
    def post(self, request):
        form = LoginUserForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            user_id = User.objects.get(username=username).id
            return redirect('home', user_id)
        else:
            users = User.objects.filter(is_staff=False)
            context = {
                'form': form
            }
            return render(request, self.temlate_name, {'UsErS': users, 'context': context})

class RegistrationPage(View):
    """ Страница регистрации """
    temlate_name = 'registration/registration.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home', request.user.id)
        users = User.objects.filter(is_staff=False)
        context = {
            'form': RegistrationForm
        }
        return render(request, self.temlate_name, {'UsErS': users, 'context': context})
    
    def post(self, request):
        form = RegistrationForm(request.POST, request.FILES)
        users = User.objects.filter(is_staff=False)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            photo = form.cleaned_data.get('photo')
            user = authenticate(username=username, password=password)
            login(request, user)
            user_id = User.objects.get(username=username).id
            u = Users(user=User.objects.get(username=username), Photo=photo)
            u.save()
            u.Friends.add(u)
            u.save()
            return redirect('home', user_id)
        else:
            context = {
                'form': form
            }
            return render(request, self.temlate_name, {'UsErS': users, 'context': context})

class HomePage(APIView):
    
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "Messenger/home_page.html"

    def get(self, request, pk):
        if request.user.id == pk:
            Logged_Client = get_object_or_404(User, pk=pk)
            Client_serialiser = Serializers.UserSerializer(Logged_Client)
            Users = Logged_Client.users.Friends.all()
            Users_with_unreaded_messages = {}
            for user in Users:
                U_serialiser = Serializers.UsersSerializer(user)
                amount = list(Private_Log.objects.filter(From_User=user.user, To_User=Logged_Client, Status=False).values_list('id', flat=True))
                Users_with_unreaded_messages[U_serialiser] = amount.__len__()
            return Response(data={"Client": Client_serialiser, 'UsErS': Users_with_unreaded_messages})

class UserMessages(APIView):
    """ Сообщения пользователя """
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "Messenger/user_messages.html"
    messages_to_load = 25

    def get(self, request, client_pk, companion_pk):
        if request.user.id == client_pk:
            Logged_Client = get_object_or_404(User, pk=client_pk)
            Client_serialiser = Serializers.MessagesPageUserSerializer(Logged_Client)
            companion = get_object_or_404(User, pk=companion_pk)
            Companion_serialiser = Serializers.MessagesPageUserSerializer(companion)
            Log = Private_Log.objects.filter(From_User__in=[Logged_Client, companion], To_User__in=[Logged_Client, companion])

            if request.GET.get('type') == 'update':
                New_messages = list(Log.filter(id__lt=int(request.GET.get('value'))).order_by('-id')[:self.messages_to_load])
                UPD_log = Serializers.UpdateLogSerializer(New_messages, many=True)
                return HttpResponse(JSONRenderer().render(UPD_log.data))
            
            unreaded_count = Log.filter(From_User=companion, To_User=Logged_Client, Status=False).__len__()
            Log = Log.order_by('-id')[:unreaded_count+self.messages_to_load:-1]
            logSerializer = Serializers.LogSerializer(Log, many=True)
            Users = Logged_Client.users.Friends.all()
            Users_with_unreaded_messages = {}
            for user in Users:
                U_serialiser = Serializers.UsersSerializer(user)
                amount = list(Private_Log.objects.filter(From_User=user.user, To_User=Logged_Client, Status=False).values_list('id', flat=True))
                Users_with_unreaded_messages[U_serialiser] = amount.__len__()
            return Response(data={"Client": Client_serialiser, "Companion": Companion_serialiser, 'UsErS': Users_with_unreaded_messages, "Log": logSerializer})

class SettingsPage(APIView):
    
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, HTMLFormRenderer]
    parser_classes = [MultiPartParser, FormParser]
    template_name = "Messenger/settings.html"

    def get(self, request, pk):
        if request.user.id == pk:
            Logged_Client = get_object_or_404(User, pk=pk)
            serializer = Serializers.SettingSerializer(Logged_Client)
            Client_serialiser = Serializers.MessagesPageUserSerializer(Logged_Client)
            Users = Logged_Client.users.Friends.all()
            Users_with_unreaded_messages = {}
            for user in Users:
                U_serialiser = Serializers.UsersSerializer(user)
                amount = list(Private_Log.objects.filter(From_User=user.user, To_User=Logged_Client, Status=False).values_list('id', flat=True))
                Users_with_unreaded_messages[U_serialiser] = amount.__len__()
            return Response(data={"Client": Client_serialiser, 'UsErS': Users_with_unreaded_messages, 'serializer': serializer})
        
    def post(self,request, pk):
        if request.user.id == pk:
            Logged_Client = get_object_or_404(User, pk=pk)
            serializer = Serializers.SettingSerializer(Logged_Client, data=request.data)
            serializer.is_valid()
            serializer.save()
            login(request, Logged_Client)
            serializer = Serializers.SettingSerializer(Logged_Client) #??????????
            Client_serialiser = Serializers.MessagesPageUserSerializer(Logged_Client)
            Users = Logged_Client.users.Friends.all()
            Users_with_unreaded_messages = {}
            for user in Users:
                U_serialiser = Serializers.UsersSerializer(user)
                amount = list(Private_Log.objects.filter(From_User=user.user, To_User=Logged_Client, Status=False).values_list('id', flat=True))
                Users_with_unreaded_messages[U_serialiser] = amount.__len__()
            return Response(data={"Client": Client_serialiser, 'UsErS': Users_with_unreaded_messages, 'serializer': serializer})

class DeleteFriend(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Serializers.UsersSerializerAll
    queryset = Users.objects.all()

    def get(self, request, client_pk, delete_pk):
        if request.user.id == client_pk and client_pk != delete_pk:
            user = self.queryset.filter(user_id=client_pk)
            del_user = self.queryset.filter(user_id=delete_pk)
            user[0].Friends.remove(del_user[0])
            
            ref_id = re.findall(r'to_user_id=(\d+)', request.META['HTTP_REFERER'])
            if ref_id and int(ref_id[0]) == delete_pk:
                return redirect('home', client_pk)
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

class DeleteAccount(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get(self, request, pk):
        if request.user.id == pk:
            instance = self.get_object()
            self.perform_destroy(instance)
            logout(request)
            return redirect("login")
        
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Serializers.UserCheckSerializer
    permission_classes = [IsAdminUser]

class LogViewSet(viewsets.ModelViewSet):
    queryset = Private_Log.objects.all()
    serializer_class = Serializers.LogSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(From_User__in=[20, 11], To_User__in=[20, 11]).filter(id__lt=50).order_by('-id')
        return super().list(request, *args, **kwargs)

class DelViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter()
    serializer_class = Serializers.SettingSerializer
    
@login_required
def LogoutUser(request):
    logout(request)
    return redirect("login")

def redirect_view(request):
    return redirect("login")

@login_required
def add_friend(request, pk):
    user = User.objects.get(id=pk).users
    user.Friends.add(request.GET['friend_id'])
    return HttpResponseRedirect(request.GET['prev'])