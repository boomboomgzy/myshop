from myshop.apps.orders import views
from django.urls import path

app_name='orders'


urlpatterns = [
    path('orders/comment/',views.OrderCommentView.as_view(),name='order_comment'),
    path('orders/comment/<sku_id>',views.SkuCommentView.as_view(),name='sku_comment'),
    path('orders/computation/',views.OrderComputation.as_view(),name='order_computation'),
    path('orders/confirm/',views.OrderConfirmView.as_view(),name='order_confirm'),
    path('orders/commit/',views.OrderCommitView.as_view(),name='order_commit'),
]

