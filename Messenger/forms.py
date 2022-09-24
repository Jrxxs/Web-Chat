from multiprocessing import AuthenticationError
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Private_Log


class MessageForm(forms.ModelForm):
    """ Форма сообщений  """
    class Meta:
        model = Private_Log
        fields = ('Message',)

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))