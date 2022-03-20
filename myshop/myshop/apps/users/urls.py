from . import views
from django.urls import path, register_converter
from myshop.utils.convertors import UsernameConverter,MobileConverter


app_name='users'

register_converter(UsernameConverter,'check_username')
register_converter(MobileConverter,'check_mobile')

urlpatterns = [
    path('namecounts/<check_username:username>/',views.UsernameCountView.as_view(),name='namecount'),
    path('mobilecounts/<check_mobile:mobile>/',views.MobileCountView.as_view(),name='mobilecount'),
    path('register/',views.RegisterView.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('emails/',views.EmailView.as_view(),name='emails'),
    path('emails/verifications/',views.VerifyEmailView.as_view(),name='emails_verification'),
    path('info/',views.UserInfoView.as_view(),name='info'),
    path('password/',views.UserPasswordView.as_view(),name='password'),
    path('addresses/',views.AddressView.as_view(),name='address'),
    path('addresses/create/',views.CreateAddressView.as_view(),name='create_address'),
    path('addresses/<int:address_id>/',views.UpdateOrDeleteAddressView.as_view(),name='updateordelete_address'),
    path('addresses/<int:address_id>/default/',views.DefaultAddressView.as_view(),name='set_default_address'),
    path('addresses/<int:address_id>/title/',views.UpdateTitleAddressView.as_view(),name='update_title_address'),
]
