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
    PAY_METHOD_CHOICES=(
        (1,'CASH'),#货到付款
        (2,'ALIPAY')
    )
    ORDER_STATU_CHOICES=(
        (0, "已取消"),
        (1, "待支付"),
        (2, "待发货"),
        (3, "待收货"),
        (4, "待评价"),
        (5, "已完成"),
    )
    
    order_id=models.CharField(max_length=64,primary_key=True,verbose_name='订单号')
    user=models.ForeignKey(User,related_name='orders',on_delete=models.PROTECT,verbose_name='下单用户')
    address=models.ForeignKey(Address,on_delete=models.PROTECT,verbose_name='收货地址')
    total_count=models.IntegerField(default=0,verbose_name='商品总数')
    total_amount=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品总金额')
    send_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='运费')
    pay_method=models.SmallIntegerField(choices=PAY_METHOD_CHOICES,default=1,verbose_name='支付方式')
    status=models.SmallIntegerField(choices=ORDER_STATU_CHOICES,default=1,verbose_name='订单状态')
    
    class Meta:
        db_table='myshop_order'
        verbose_name='订单信息'
        verbose_name_plural=verbose_name
    
    def __str__(self):
        return self.order_id
    
class OrderSku(ExtendModel):
    
    order=models.ForeignKey(Order,related_name='skus',on_delete=models.CASCADE,verbose_name='所属订单')
    sku=models.ForeignKey(SKU,on_delete=models.PROTECT,verbose_name='订单商品')
    count=models.IntegerField(default=1,verbose_name='数量')
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='单价')
    comment=models.TextField(default="",verbose_name='评价')
    comment_is_anonymous=models.BooleanField(default=False,verbose_name="是否匿名评价")
    is_commented=models.BooleanField(default=False,verbose_name='是否已经评论')
    
    
    class Meta:
        db_table='myshop_order_sku'
        verbose_name='订单商品'
        verbose_name_plural=verbose_name
        
    def __str__(self):
        return self.sku.name
    