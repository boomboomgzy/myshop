from atexit import register
from . import views
from django.urls import path, register_converter
from myshop.utils.convertors import UsernameConverter
app_name='users'

register_converter(UsernameConverter,'username')

urlpatterns = [
    path('usernamecounts/<username:check_username>',views.UsernameCountView.as_view(),name='usernamecount'),
    path('register/',views.RegisterView.as_view(),name='register')
]
