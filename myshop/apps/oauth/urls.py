from myshop.apps.oauth import views
from django.urls import path

app_name='oauth'


urlpatterns = [
    path('baidu/login/',views.BaiduLoginView.as_view(),name='baidu_login'),
    path('baidu/oauth_backend/',views.BaiduOauthBackEndView.as_view(),name='baidu_oauth_backend'),
]


