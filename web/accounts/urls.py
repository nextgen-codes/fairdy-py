from django.contrib.auth.views import LoginView
from django.urls import path

from .views import *

app_name = 'accounts'

urlpatterns = [
    path('user_index/', user_index, name='user_index'),
    path('user_edit/', user_edit, name='user_edit'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('change_username/', change_username, name='change_username'),
    path('change_email/', change_email, name='change_email'),
    path('change_password/', change_password, name='change_password'),
    path('reset_password/<token>/', reset_password, name='reset_password'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('delete/', delete, name='delete'),
    path('profile/', profile, name='profile'),
    path('validate/<token>/', validate_email, name='validate'),
    path('resend_validation', resend_validation, name='resend_validation'),
    path('help/create_account/', help_create_account, name='help_create_account'),
    path('help/manage_account/', help_manage_account, name='help_manage_account'),
    path('help/manage_users/', help_manage_users, name='help_manage_users'),
]
