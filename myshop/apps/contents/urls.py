from myshop.apps.contents import views
from django.urls import path

app_name='contents'


urlpatterns = [
    path('contents/index/',views.IndexView.as_view(),name='contents_index'),
]