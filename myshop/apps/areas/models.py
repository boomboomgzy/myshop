from django.db import models

# Create your models here.

class Area(models.Model):
    #地址模型
    
    name=models.CharField(max_length=20,verbose_name='名称')
    parent=models.ForeignKey('self',on_delete=models.SET_NULL,related_name='sub_areas',null=True,verbose_name='上级行政区域')

    

    class Meta:
        db_table='myshop_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name
