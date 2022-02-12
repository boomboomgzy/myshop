from django.db import models
from myshop.utils.models import ExtendModel

class GoodsCategory(ExtendModel):
    #货物有三个级别的分类
    name=models.CharField(max_length=10,verbose_name='名称')
    parent=models.ForeignKey('self',null=True,on_delete=models.CASCADE,verbose_name='父类别')

    class Meta:
        db_table='myshop_goods_category'
        verbose_name='商品类别'
        verbose_name_plural=verbose_name
        
    def __str__(self):
        return self.name
    
 
class GoodsChannel(ExtendModel):
    #商品频道 
    
    group_id=models.IntegerField(verbose_name='组号')
    #频道即为商品的一级分类
    category=models.ForeignKey(GoodsCategory,on_delete=models.CASCADE)
    url=models.CharField(max_length=50,verbose_name='频道页面')
    sequence=models.IntegerField(verbose_name='组内序号')
    
    class Meta:
        db_table='myshop_goods_channel'
        verbose_name='商品频道'
        verbose_name_plural=verbose_name
        
    def __str__(self):
        return self.category.name
        
        
class Brand(ExtendModel):
    
    name=models.CharField(max_length=20,verbose_name='名称')
    logo=models.ImageField(verbose_name='logo')
    first_letter=models.CharField(max_length=1,verbose_name='首字母')
    
    class Meta:
        db_table='myshop_brand'
        verbose_name='品牌'
        verbose_name_plural=verbose_name
        
    def __str__(self):
        return self.name
    
    
#一个商品包含了不同规格
class Goods(ExtendModel):
    #该商品名称
    name=models.CharField(max_length=50,verbose_name='名称')
    #该商品品牌
    brand=models.ForeignKey(Brand,on_delete=models.PROTECT,verbose_name='品牌')
    #该商品的一级分类
    category1=models.ForeignKey(GoodsCategory,related_name='goods_by_category1',on_delete=models.PROTECT,verbose_name='category1')
    #该商品的二级分类
    category2=models.ForeignKey(GoodsCategory,related_name='goods_by_category2',on_delete=models.PROTECT,verbose_name='category2')
    #该商品的三级分类
    category3=models.ForeignKey(GoodsCategory,related_name='goods_by_category3',on_delete=models.PROTECT,verbose_name='category3')
    #该商品销量
    sale_count=models.IntegerField(default=0,verbose_name='销量')
    #该商品评论数
    comment_count=models.IntegerField(default=0,verbose_name='评论数')
    
class GoodsSpecification(ExtendModel):
    #商品的规格 如：颜色、尺寸
    
    #该规格对应的商品
    goods=models.ForeignKey(Goods,on_delete=models.CASCADE,verbose_name='商品')
    
    name=models.CharField(max_length=20,verbose_name='规格名称')
    
    class Meta:
        db_table='myshop_goods_specification'
        verbose_name='商品规格'
        verbose_name_plural=verbose_name
    
    def __str__(self):
        return self.goods.name+' : '+self.name
    
    
class SpecificationOption(ExtendModel):
    #规格的选项 如：颜色的蓝色、红色
    
    spec=models.ForeignKey(GoodsSpecification,on_delete=models.CASCADE,verbose_name='规格')
    value=models.CharField(max_length=20,verbose_name='选项值')
    
    class Meta:
        db_table='myshop_specification_option'
        verbose_name='规格选项'
        verbose_name_plural=verbose_name
        
    def __str__(self):
        return self.spec+' : '+self.value
    
class SKU(ExtendModel):
    #具体的单个商品
    
    name=models.CharField(max_length=50,verbose_name='商品名称')
    caption=models.CharField(max_length=100,verbose_name='副标题')
    #所属商品
    goods=models.ForeignKey(Goods,on_delete=models.CASCADE,verbose_name='所属商品')
    category=models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,verbose_name='类别')
    sale_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='销售单价')
    cost_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='成本单价')
    market_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='市场价')
    #库存
    stock=models.IntegerField(default=0,verbose_name='库存')
    #销量
    sale_count=models.IntegerField(default=0,verbose_name='销量')
    comment_count=models.IntegerField(default=0,verbose_name='评论数')
    #是否在售
    is_onsale=models.BooleanField(default=True,verbose_name='是否在售')
    #该商品默认照片
    default_image_url=models.CharField(max_length=200,null=True,verbose_name='商品默认图片')
    
    class Meta:
        db_table='myshop_sku'
        verbose_name='sku'
        verbose_name_plural=verbose_name
    
    def __str__(self):
        return self.name
    
    
class SKUImage(ExtendModel):
    
    sku=models.ForeignKey(SKU,on_delete=models.CASCADE,verbose_name='sku')
    image=models.ImageField(verbose_name='图片')
    
    class Meta:
        db_table='myshop_sku_image'
        verbose_name='sku图片'
        verbose_name_plural=verbose_name
        
class SKUSpecification(ExtendModel):
    
    # 对应的SKU值
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='sku')
    # 对应哪一个规格
    spec = models.ForeignKey(GoodsSpecification, on_delete=models.PROTECT, verbose_name='规格名称')
    # 规格的具体内容
    option = models.ForeignKey(SpecificationOption, on_delete=models.PROTECT, verbose_name='规格值')

    class Meta:
        db_table = 'tb_sku_specification'
        verbose_name = 'SKU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku+self.spec.name+self.option.value
    
    
    
    
    
    
    
    