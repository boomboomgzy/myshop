#图形验证码过期时间 单位：S
IMG_CODE_REDIS_EXPIRES=180

#容联云短信验证码过期时间 单位：s
SMS_CODE_REDIS_EXPIERS=5*60

#容联云短信发送间隔时间 单位: s
SMS_CODE_REDIS_INTERVAL=60

#邮件校验令牌过期时间 单位：S
VERIFY_EMAIL_TOKEN_EXPIRES=10*60

#redis地址缓存过期时间 单位：S
MYSHOP_REDIS_AREAS_EXPIRES=60*60

#minio url过期时间 单位：S
MINIO_URL_EXPIERS=60*60*24

#用户session登录状态保存时间 单位：s
USER_SESSION_EXPIRES=60*60*24*3

#用户名cookie有效时间 单位：s
USERNAME_COOKIE_EXPIRES=60*60*24

#收货地址的最大个数
USER_ADDRESS_COUNT_LIMIT=20

#容联云
rongLianYun_accId='8aaf07087e7b9872017e865a4c020155'
rongLianYun_accToken='82e0c70222324753a0c4d96e2f695257'
rongLianYun_appId='8aaf07087e7b9872017e865a4d16015b'
rongLianYun_tid='1'

#显示货物时每页5条记录
GOODS_LIST_LIMIT=5


# order 

#订单状态词典
ORDER_STATUS={
    'CANCELED':0,
    'UNPAID':1,
    'UNSEND':2,#现金支付
    'UNRECEIVED':3,
    'UNCOMMENT':4,
    'FINISHED':5
}
#订单支付手段词典
ORDER_PAY_METHOD={
    'CASH':1,
    'ALIPAY':2
}

#运费
ORDER_FREIGHT='10.00'
#订单每页显示5条
ORDER_SHOW_LIMIT=5
#baidu openid加密token有效时间 单位:s
BAIDU_MYSHOP_TOKEN_EXPIRES=600






class HtmlTemplate(object):
    """
    项目 html网页模板路径汇总类
    """

    # 首页
    INDEX_HTML = 'index.html'

    """
    用户登录模块
    """
    # 用户登录
    LOGIN_HTML = 'users/login.html'

    # 用户注册
    REGISTER_HTML = 'users/register.html'

    # 用户中心个人信息
    USER_CENTER_INFO_HTML = 'users/user_center_info.html'

    # 用户中心收货地址
    USER_CENTER_ADDRESS_HTML = 'users/user_center_site.html'

    # 用户中心订单页面
    USER_CENTER_ORDER = 'users/user_center_order.html'

    # 用户中心修改密码
    USER_CENTER_PASS_HTML = 'users/user_center_pass.html'

    """
    OAuth 模块
    """
    # OAuth 第三方登录用户绑定
    OAUTH_CALLBACK_HTML = 'oauth/oauth_callback.html'

    """
    商品模块
    """
    # 商品列表
    GOODS_LIST_HTML = 'goods/list.html'

    # 商品详情
    GOODS_DETAIL_HTML = 'goods/detail.html'

    """
    全文检索模块
    """
    # 全文检索回调的 search.html
    SEARCH_HTML = 'search/search.html'

    """
    购物车模块
    """
    # 购物车列表
    CART_LIST_HTML = 'carts/cart.html'

    """
    订单模块
    """
    # 订单结算界面
    ORDER_PLACE_HTML = 'orders/place_order.html'

    # 订单提交成功页面
    ORDER_SUCCESS_HTML = 'orders/order_success.html'

    """
    支付模块
    """
    # 订单支付成功页面
    PAY_SUCCESS_HTML = 'payment/pay_success.html'

    """
    项目错误 html 模板
    """
    ERRORS_404_HTML = 'errors/404.html'


class CookieKey(object):
    
    #用户名cookie
    USERNAME_KEY='username'


class Rediskey(object):
    
    IMG_CODE_KEY='myshop_img_code_{uuid}'
    
    SMS_CODE_KEY='myshop_sms_code_{mobile}'
    
    SMS_SEND_FLAG_KEY='myshop_sms_send_flag_{mobile}'

    #省级地址数据 key
    PROVINCES_LIST_KEY='myshop_provinces_list'
    
    #子地址数据 key
    SUB_AREAS_LIST_KEY='myshop_sub_areas_list_{area_id}'    
    
    #用户购物车数量数据 key
    USER_CARTS_COUNT_KEY='myshop_carts_count_{user_id}'
    
    #用户购物车选中数据 key
    USER_CARTS_SELECT_KEY='myshop_carts_select_{user_id}'   
    
#REDIS 购物车数据示例
'''
'USER_CARTS_COUNT_KEY':{
    'sku.id':5
}
'USER_CARTS_SELECT_KEY':{
   'sku.id':'True'
}

'''  
    