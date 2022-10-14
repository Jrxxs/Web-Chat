from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, login, authenticate

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
            return render(request, "Messenger/home_page.html", {"Client": Logged_Client, 'UsErS': Users})

class UserMessages(LoginRequiredMixin, View):
    """ Сообщения пользователя """
    def get(self, request, client_pk, companion_pk):
        if request.user.id == client_pk:
            Logged_Client = User.objects.get(id=client_pk)
            companion = User.objects.get(id=companion_pk)
            Log = Private_Log.objects.filter(From_User__in=[Logged_Client, companion], To_User__in=[Logged_Client, companion])
            Users = Logged_Client.users.Friends.all()
            return render(request, "Messenger/user_messages.html", {"Client": Logged_Client, "Companion": companion, 'UsErS': Users, "Log": Log})
    
def LogoutUser(reqest):
    logout(reqest)
    return redirect("login")

def redirect_view(reqest):
    return redirect("login")

# class SendMessage(View):
#     """ Сообщения """
#     def post(self, request, client_pk, companion_pk):
#         form = MessageForm(request.POST)
#         Client = User.objects.get(id=client_pk)
#         Companion = User.objects.get(id=companion_pk)
#         if form.is_valid():
#             form = form.save(commit=False)
#             form.From_User = Client
#             form.To_User = Companion
#             form.save()
#         return redirect(reverse("user_messages", kwargs={"client_pk": Client.id, "companion_pk": Companion.id}))

    #      SECOND WAY ----->  finding users by their pk's
    # def post(self, request, client_pk, companion_pk):
    #     form = MessageForm(request.POST)
    #     if form.is_valid():
    #         form = form.save(commit=False)
    #         form.From_User_id = client_pk
    #         form.To_User_id = companion_pk
    #         form.save()
    #     return redirect("/")
