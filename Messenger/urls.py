from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
router.register(r'log', views.LogViewSet)
router.register(r'del', views.DelViewSet)

urlpatterns = [
    path("", views.redirect_view),
    path("login/", views.LoginPage.as_view(), name="login"),
    path("logout/", views.LogoutUser, name="logout"),
    path("registration/", views.RegistrationPage.as_view(), name="registration"),
    path("user_id=<int:pk>/", views.HomePage.as_view(), name="home"),
    path("user_id=<int:pk>/settings/", views.SettingsPage.as_view(), name="settings"),
    path("user_id=<int:pk>/delete_account/", views.DeleteAccount.as_view(), name="del_acc"),
    path("user_id=<int:client_pk>/to_user_id=<int:companion_pk>/", views.UserMessages.as_view(), name="user_messages"),
    path("user_id=<int:client_pk>/delete_id=<int:delete_pk>/", views.DeleteFriend.as_view(), name="delete_friend"),
    path("user_id=<int:pk>/add_friend", views.add_friend, name="add_new_friend"),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
