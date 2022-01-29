from . import views
from django.urls import path


app_name='areas'

urlpatterns = [
    path('areas/',views.AreasView.as_view(),name='areas'),
]