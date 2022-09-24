from django.urls import path

from . import views

urlpatterns = [
    path("", views.redirect_view),
    path("login/", views.LoginPage.as_view(), name="login"),
    path("logout/", views.LogoutUser, name="logout"),
    path("registration/", views.RegistrationPage.as_view(), name="registration"),
    path("user_id=<int:pk>/", views.HomePage.as_view(), name="user_id"),
    path("to_user_id=<int:pk>/", views.HomePage.as_view(), name="to_user"),
    path("user_id=<int:client_pk>/to_user_id=<int:companion_pk>/", views.UserMessages.as_view(), name="user_messages"),
    # path("send/user_id=<int:client_pk>/to_user_id=<int:companion_pk>/", views.SendMessage.as_view(), name="send_message"),
]
