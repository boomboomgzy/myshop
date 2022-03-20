from myshop.apps.orders import views
from django.urls import path

app_name='orders'


urlpatterns = [
    path('comment/',views.OrderCommentView.as_view(),name='comment'),
    path('comment/<sku_id>/',views.SkuCommentView.as_view(),name='sku_comment'),
    path('computation/',views.OrderComputation.as_view(),name='computation'),
    path('commit/',views.OrderCommitView.as_view(),name='commit'),
    path('info/<int:page_num>/',views.UserOrderInfoView.as_view(),name='info'),
    path('success/',views.OrderSuccessView.as_view(),name='success')
]

