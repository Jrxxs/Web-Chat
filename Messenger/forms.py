from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class LoginUserForm(AuthenticationForm):
    """ Форма авторизации """
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

class RegistrationForm(UserCreationForm):
    """ Форма регистрации """
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    photo = forms.FileField(label="Photo", required=False)