import re
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import login
from django.views import View
from flask import redirect
from myshop.apps.oauth.models import OauthBaiduUser
from myshop.apps.users.models import User
from myshop.utils.constants import CookieKey, Rediskey
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.result import R
from myshop.utils.exceptions import BusinessException
from myshop.utils.constants import CookieKey,USERNAME_COOKIE_EXPIRES
from baidu_api import *
from django_redis import get_redis_connection

# /baidu/login/
class BaiduLoginView(View):
    def get(req,self):
        #返回百度登录地址
        #state 登录前所在url
        state=req.GET.get('state')
        
        login_url=settings.BAIDU_LOGIN_URL+f'&state={state}'
        res=R.ok().data(**{
            'login_url':login_url
        })
        
        return JsonResponse(res)
    
# /baidu/oauth_backend/
#处理登录逻辑
class BaiduOauthBackEndView(View):
       
    def get(self,req):
        code=req.GET.get('code')
        if not code:
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        access_token=get_baidu_access_token(code)
        baidu_openid=get_baidu_user_openid(access_token)
        
        state=req.GET.get('state')
        
        try:
            baidu_user=OauthBaiduUser.objects.get(baidu_openid=baidu_openid)
        except Exception as e:
            #未绑定商城用户,返回加密后的openid(即myshop_token)待用户注册后进行绑定
            myshop_token=encrypt_baidu_openid(baidu_openid)
            res=R.ok().data(**{
                'myshop_token':myshop_token,
                'state':state
            })
            return JsonResponse(res)
        else:
            #绑定了商城用户
            user=baidu_user.user
            login(req,user)
            
            res=redirect(state)    
            res.set_cookie(CookieKey.USERNAME_KEY, user.username, max_age=USERNAME_COOKIE_EXPIRES)
            
            return res
        
    def post(self,req):
        #处理用户绑定openid
        mobile = req.POST.get('mobile')
        pwd = req.POST.get('password')
        sms_code_client = req.POST.get('sms_code')
        myshop_token = req.POST.get('myshop_token')
        state=req.POST.get('state')
        
        if not all([mobile,pwd,sms_code_client,myshop_token]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            raise BusinessException(StatusCodeEnum.MOBILE_ERR)

        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            raise BusinessException(StatusCodeEnum.PWD_ERR)
        
        redis_cli=get_redis_connection(settings.VERIFY_CODE_CACHE_ALIAS)
        sms_code_key=Rediskey.SMS_CODE_KEY.format(mobile=mobile)
        sms_code_server=redis_cli.get(sms_code_key)
        
        if sms_code_server is None or sms_code_client!=sms_code_server:
            #验证码错误
            pass
        
        baidu_openid=decrypt_myshop_token(myshop_token)
        if not baidu_openid:
            #openid无效 绑定失败
            pass
        
        try:
            user=User.objects.get(mobile=mobile)
        except Exception as e:
            logger.error(e)
            user=User.objects.create_user(username=mobile,password=pwd,mobile=mobile)
        else:
            if not user.check_password(pwd):
                #用户存在但密码错误
                pass
        
        OauthBaiduUser.objects.create(baidu_openid=baidu_openid,user=user)
        
        login(req,user)
        
        res=redirect(state)
        
        res.set_cookie(CookieKey.USERNAME_KEY, user.username, max_age=USERNAME_COOKIE_EXPIRES)
        
        return res