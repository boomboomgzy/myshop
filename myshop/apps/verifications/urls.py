from . import views
from django.urls import path,register_converter
from myshop.utils.convertors import MobileConverter
app_name='verifications'


register_converter(MobileConverter,'mobile')
urlpatterns = [
    path('image_codes/<uuid:uuid>',views.ImageCodeView.as_view(),name='image_codes'),
    path('sms_codes/<mobile:mobile>',views.SmsCodeView.as_view(),name='sms_codes'),
]
