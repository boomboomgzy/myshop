from myshop.apps.carts import views
from django.urls import path

app_name='carts'


urlpatterns = [
    path('',views.CartsView.as_view(),name='info'),
    path('selection/',views.CartsSelectAllView.as_view(),name='selectall'),
]