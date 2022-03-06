from tabnanny import verbose
from django.db import models
from myshop.utils.models import ExtendModel

class ContentCategory(ExtendModel):
    
    name=models.CharField(max_length=50,verbose_name='名称')
    key=models.CharField(max_length=50,verbose_name='键名')
    
    class Meta:
        db_table='myshop_content_category'
        verbose_name='广告内容类别'
        verbose_name_plural=verbose_name
        
    def __str__(self):
        return self.name
    
class Content(ExtendModel):
    
    category=models.ForeignKey(ContentCategory,related_name='contents',on_delete=models.PROTECT,verbose_name='类别')
    title=models.CharField(max_length=100,verbose_name='标题')
    url=models.CharField(max_length=300,verbose_name='链接')
    image=models.ImageField(null=True,verbose_name='图片')
    text=models.TextField(null=True,verbose_name='内容')
    sequence=models.IntegerField(verbose_name='序号')
    status=models.BooleanField(default=True,verbose_name='展示标识')
    
    class Meta:
        db_table='myshop_contents'
        verbose_name='广告内容'
        verbose_name_plural=verbose_name
        
    def __str__(self):
        return self.category.name+':'+self.title
    
    
    
    
    