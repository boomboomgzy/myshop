from tabnanny import verbose
from django.db import models
from myshop.utils.models import ExtendModel
from myshop.apps.order.models import  Order
#֧����Ϣ
class Payment(ExtendModel):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,verbose_name='����')
    #������ˮ��
    trade_id=models.CharField(max_length=100,unique=True,null=True,verbose_name='������ˮ��')
    
    class Meta:
        db_table='myshop_payment'
        verbose_name='֧����Ϣ'
        verbose_name_plural=verbose_name
        
