from django.db import models

class ExtendModel(models.Model):
    #扩展model类
    
    create_time=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time=models.DateTimeField(auto_now=True,verbose_name='更新时间')
    
    class Meta:
        abstract=True