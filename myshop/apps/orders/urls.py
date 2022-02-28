from myshop.apps.orders import views
from django.urls import path

app_name='orders'


urlpatterns = [
    path('orders/comment/',views.OrderCommentView.as_view(),name='order_comment'),
    path('orders/comment/<sku_id>',views.SkuCommentView.as_view(),name='sku_comment'),
    path('orders/computation/',views.OrderComputation.as_view(),name='order_computation'),
    path('orders/commit/',views.OrderCommitView.as_view(),name='order_commit'),
    path('orders/info/<int:page_num>',views.UserOrderInfoView.as_view(),name='user_order_info'),
]

