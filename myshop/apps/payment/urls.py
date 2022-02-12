from payment import views
from django.urls import path

app_name='payment'


urlpatterns = [
    path('payment/<order_id>',views.PaymentView.as_view(),name='pay_order'),
    path('payment/status/',views.PaymentStatusView.as_view(),name='order_status')
    
]



