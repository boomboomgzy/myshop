from myshop.apps.payment import views
from django.urls import path

app_name='payment'


urlpatterns = [
    path('status/',views.PaymentStatusView.as_view(),name='order_status'),
    path('<order_id>/',views.PaymentView.as_view(),name='pay_order'),
]



