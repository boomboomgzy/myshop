from . import views
from django.urls import path


app_name='areas'

urlpatterns = [
    path('',views.AreasView.as_view(),name='areas'),
]