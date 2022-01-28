from . import views
from django.urls import path, register_converter
from myshop.utils.convertors import UsernameConverter


app_name='users'

register_converter(UsernameConverter,'username')

urlpatterns = [
    path('usernamecounts/<username:check_username>',views.UsernameCountView.as_view(),name='usernamecount'),
    path('register/',views.RegisterView.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('emails/',views.EmailView.as_view(),name='emails'),
    path('emails/verifications',views.VerifyEmailView.as_view(),name='emails_verification'),
    path('info/',views.UserInfoView.as_view(),name='info'),
]
