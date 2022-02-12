from itertools import count
from operator import mod
from tabnanny import verbose
from xml.etree.ElementTree import Comment
from django.db import models
from myshop.utils.constants import ORDER_PAY_METHOD
from myshop.utils.models import ExtendModel
from myshop.apps.users.models import User,Address
from myshop.apps.goods.models import SKU

class Order(ExtendModel):
    PAY_METHOD_CHOICES={
        (1,'CASH'),#��������
        (2,'ALIPAY')
    }
    ORDER_STATU={
        (0, "��ȡ��"),
        (1, "��֧��"),
        (2, "������"),
        (3, "���ջ�"),
        (4, "������"),
        (5, "�����"),
    }
    
    order_id=models.CharField(max_length=64,primary_key=True,verbose_name='������')
    user=models.ForeignKey(User,related_name='orders',on_delete=models.PROTECT,verbose_name='�µ��û�')
    address=models.ForeignKey(Address,on_delete=models.PROTECT,verbose_name='�ջ���ַ')
    total_count=models.IntegerField(default=0,verbose_name='��Ʒ����')
    total_amount=models.IntegerField(max_digits=10,decimal_places=2,verbose_name='��Ʒ�ܽ��')
    send_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='�˷�')
    pay_method=models.SmallIntegerField(choices=ORDER_PAY_METHOD,default=1,verbose_name='֧����ʽ')
    status=models.SmallIntegerField(choices=ORDER_STATU,default=1,verbose_name='����״̬')
    
    class Meta:
        db_table='myshop_order'
        verbose_name='������Ϣ'
        verbose_name_plural=verbose_name
    
    def __str__(self):
        return self.order_id
    
class OrderSku(ExtendModel):
    
    order=models.ForeignKey(Order,related_name='order_skus',on_delete=models.CASCADE,verbose_name='��������')
    sku=models.ForeignKey(SKU,on_delete=models.PROTECT,verbose_name='������Ʒ')
    count=models.IntegerField(default=1,verbose_name='����')
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='����')
    comment=models.TextField(default="",verbose_name='����')
    comment_is_anonymous=models.BooleanField(default=False,verbose_name="�Ƿ���������")
    is_commented=models.BooleanField(default=False,verbose_name='�Ƿ��Ѿ�����')
    
    
    class Meta:
        db_table='myshop_order_sku'
        verbose_name='������Ʒ'
        verbose_name_plural=verbose_name
        
    def __str__(self):
        return self.sku.name
    