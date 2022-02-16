from myshop.apps.carts import views
from django.urls import path

app_name='carts'


urlpatterns = [
    path('carts/',views.CartsView.as_view(),name='carts'),
]