from myshop.apps.goods import views
from django.urls import path

app_name='goods'


urlpatterns = [
    path('list/<int:category_id>/<int:page_num>/',views.ListView.as_view(),name='list'),
    path('hot/<int:category_id>/',views.HotGoodsView.as_view(),name='hot'),
    path('detail/<int:sku_id>/',views.DetailView.as_view(),name='detail'),
]


