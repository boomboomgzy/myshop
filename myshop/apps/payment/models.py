from tabnanny import verbose
from django.db import models
from myshop.utils.models import ExtendModel
from myshop.apps.order.models import  Order
#支付信息
class Payment(ExtendModel):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,verbose_name='订单')
    #交易流水号
    trade_id=models.CharField(max_length=100,unique=True,null=True,verbose_name='交易流水号')
    
    class Meta:
        db_table='myshop_payment'
        verbose_name='支付信息'
        verbose_name_plural=verbose_name
        
