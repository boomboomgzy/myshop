from tabnanny import verbose
from django.db import models
from myshop.utils.models import ExtendModel
from myshop.apps.users.models import User


class OauthBaiduUser(ExtendModel):
    user=models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='用户')
    baidu_openid=models.CharField(max_length=128,verbose_name='baidu用户id')
    
    class Meta:
        db_table='myshop_baidu_oauth'
        verbose_name='baidu登录用户数据'
        verbose_name_plural=verbose_name