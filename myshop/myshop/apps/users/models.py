from django.db import models
from myshop.apps.areas.models import Area
from django.contrib.auth.models import AbstractUser
from myshop.utils.models import ExtendModel


class Address(ExtendModel):
      #收货地址信息
      user=models.ForeignKey('users.user',verbose_name="所属用户",related_name='addresses',on_delete=models.CASCADE,null=True)
      title=models.CharField(max_length=20,verbose_name='标识')  
      receiver=models.CharField(max_length=20,verbose_name='收件人')
      province=models.ForeignKey(Area,verbose_name="省",related_name='addresses_by_province',on_delete=models.PROTECT,null=True)
      city=models.ForeignKey(Area,on_delete=models.PROTECT,related_name='addresses_by_city',null=True,verbose_name='市')
      district=models.ForeignKey(Area,on_delete=models.PROTECT,related_name='addresses_by_district',null=True,verbose_name='区')
      place=models.CharField(max_length=50,verbose_name='详细地址')
      mobile=models.CharField(max_length=11,verbose_name='收件人手机')
      tel=models.CharField(max_length=20,verbose_name='固定电话',null=True)
      email = models.CharField(max_length=30, null=True,default='', verbose_name='电子邮箱')
      is_deleted=models.BooleanField(default=False,verbose_name='删除标识')
      
      class Meta:
          db_table='myshop_addresses'
          ordering=['-update_time']
          verbose_name='收货地址'
          verbose_name_plural=verbose_name


class User(AbstractUser):
    #自定义用户模型
    
    mobile=models.CharField(
        max_length=11,
        unique=True,
        verbose_name='手机号'
        )
    email_active=models.BooleanField(default=False,
                                     verbose_name='邮箱验证状态')
    
    default_address=models.ForeignKey(Address,null=True,on_delete=models.SET_NULL,related_name='default_address',verbose_name='详细地址')
    
    class Meta:
        db_table='myshop_users'
        verbose_name='用户信息'
        verbose_name_plural=verbose_name
        ordering=['id']
        
    def __str__(self):
        return self.username


