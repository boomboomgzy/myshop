#图形验证码过期时间 单位：S
IMG_CODE_REDIS_EXPIRES=180

#容联云短信验证码过期时间 单位：m
SMS_CODE_REDIS_EXPIERS=5

#容联云短信发送间隔时间 单位: m
SMS_CODE_REDIS_INTERVAL=1

#邮件校验令牌过期时间 单位：S
VERIFY_EMAIL_TOKEN_EXPIRES=10*60

#redis地址缓存过期时间 单位：S
MYSHOP_REDIS_AREAS_EXPIRES=3600

#minio url过期时间 单位：S
MINIO_URL_EXPIERS=60*60*24

#容联云
rongLianYun_accId='8aaf07087e7b9872017e865a4c020155'
rongLianYun_accToken='82e0c70222324753a0c4d96e2f695257'
rongLianYun_appId='8aaf07087e7b9872017e865a4d16015b'
rongLianYun_tid='1'

#minio 
minio_AccessKey='minio'
minio_SecretKey='minio@123'
minio_Bucket='myshop'

# order 

#订单状态词典
ORDER_STATUS={
    'CANCELED':0,
    'UNPAID':1,
    'UNSEND':2,
    'UNRECEIVED':3,
    'UNCOMMENT':4,
    'FINISHED':5
}
#订单支付手段词典
ORDER_PAY_METHOD={
    'CASH':1,
    'ALIPAY':2
}


    
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
    
    #用户购物车数据 key
    USER_CARTS_KEY='myshop_carts_{user_id}'

#REDIS 购物车数据示例
'''
'USER_CARTS_KEY':{
    'sku.id':{
        'count':5,
        'selected':'True'  #True标识选中,False表示未选中
    }
}
'''  
    