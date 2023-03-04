from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
import re

from .models import Users, Private_Log, User
from .forms import LoginUserForm, RegistrationForm

class LoginPage(View):
    """ Страница авторизации """
    temlate_name = 'registration/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('user_id', request.user.id)
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
            return redirect('user_id', user_id)
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
            return redirect('user_id', request.user.id)
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
            return redirect('user_id', user_id)
        else:
            context = {
                'form': form
            }
            return render(request, self.temlate_name, {'UsErS': users, 'context': context})

class HomePage(LoginRequiredMixin ,View):
    """ Главная страница """
    def get(self, request, pk):
        if request.user.id == pk:
            Logged_Client = User.objects.get(id=pk)
            # users = User.objects.filter(is_staff=False)
            Users = Logged_Client.users.Friends.all()
            Users_with_unreaded_messages = {}
            for user in Users:
                amount = list(Private_Log.objects.filter(From_User=user.user, To_User=Logged_Client, Status=False).values_list('id', flat=True))
                Users_with_unreaded_messages[user] = amount.__len__()
            return render(request, "Messenger/home_page.html", {"Client": Logged_Client, 'UsErS': Users_with_unreaded_messages,})

class UserMessages(LoginRequiredMixin, View):
    """ Сообщения пользователя """
    def get(self, request, client_pk, companion_pk):
        if request.user.id == client_pk:
            Logged_Client = User.objects.get(id=client_pk)
            companion = User.objects.get(id=companion_pk)
            Log = Private_Log.objects.filter(From_User__in=[Logged_Client, companion], To_User__in=[Logged_Client, companion]).order_by('Date_Time')
            Users = Logged_Client.users.Friends.all()
            Users_with_unreaded_messages = {}
            for user in Users:
                amount = list(Private_Log.objects.filter(From_User=user.user, To_User=Logged_Client, Status=False).values_list('id', flat=True))
                Users_with_unreaded_messages[user] = amount.__len__()
            return render(request, "Messenger/user_messages.html", 
                {"Client": Logged_Client, "Companion": companion, 'UsErS': Users_with_unreaded_messages, "Log": Log})

class DeleteFriend(LoginRequiredMixin, View):

    def get(self, request, client_pk, delete_pk):
        if request.user.id == client_pk:
            user = User.objects.get(id=client_pk).users
            del_user = User.objects.get(id=delete_pk).users
            user.Friends.remove(del_user)
            ref_id = re.findall(r'to_user_id=(\d+)', request.META['HTTP_REFERER'])
            if ref_id and int(ref_id[0]) == delete_pk:
                print('xxxxxxx', delete_pk)
                return redirect('home', client_pk)
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

def LogoutUser(request):
    logout(request)
    return redirect("login")

def redirect_view(request):
    return redirect("login")

@login_required
def add_friend(request, uid):
    user = User.objects.get(id=uid).users
    user.Friends.add(request.GET['friend_id'])
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
