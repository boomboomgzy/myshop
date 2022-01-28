from asyncio.log import logger
import imp
import re
from django.conf import settings
from elasticsearch import serializer
from itsdangerous import json
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R
from myshop.utils.enums import StatusCodeEnum
from django.http import JsonResponse
from django.shortcuts import redirect, render,reverse
from .models import User
from django.views import View
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from myshop.celery_tasks.email.task import celery_send_verify_email
from itsdangerous.jws import TimedJSONWebSignatureSerializer as Serializer
from myshop.utils.constants import VERIFY_EMAIL_TOKEN_EXPIRES

#生成邮箱验证url
def generate_verify_email_url(user):
    serializer=Serializer(settings.ITSDANGEROUS_SCRETE_KEY,expire_in=VERIFY_EMAIL_TOKEN_EXPIRES)
    data={
        'user_id':user.id,
        'email':user.email
    }
    token=serializer.dump(data).decode()
    verify_url=settings.EMAIL_VERIFY_URL+'?token='+token
    
    return verify_url
#检查邮箱验证token
def check_verify_email_token(token):
    serializer=Serializer(settings.ITSDANGEROUS_SCRETE_KEY,expire_in=VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data=serializer.loads(token)
    except Exception:
        return None
    else:
        user_id=data.get('user_id')
        email=data.get('email')
        
        try:
            user=User.objects.get(id=user_id,email=email)
        except User.DoesNotExist:
            return None
        else:
            return user

    # /users/usernamecounts/<str:username>
class UsernameCountView(View):
    
    def get(self,req,check_username):
        #username检查
        count=User.objects.filter(username=check_username).count()
        
        res=R.ok().data(**{
            'username_count':count
        })
        return JsonResponse(res)
        
    # /users/register
class RegisterView(View):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.username = None
        self.password = None
        self.confirm_pwd = None
        self.mobile = None
        self.sms_code_client = None
        self.allow = None
    
    def get(self,req):
     #提供注册页面
        pass
    
    def verifi_parm(self,req):
        #接收参数
        self.username = req.POST.get('username')
        self.password = req.POST.get('password')
        self.confirm_pwd = req.POST.get('confirm_pwd')
        self.mobile = req.POST.get('mobile')
        self.sms_code_client = req.POST.get('sms_code')
        self.allow = req.POST.get('allow')
    
        all_args=[self.username,self.password,self.confirm_pwd,self.mobile,
                  self.sms_code_client,self.allow]
        
        if not all(all_args):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        #检查每个字段
            pass
        #使用 User.objects.create_user创建并保存入库（该方法对密码加入数据库时进行了加密）
        
    def post(self,req):
        #信息检查
        self.verifi_parm(req)        

# /users/login   (unfinish)
class LoginView(View):
    
    def get(self,req):
        #提供登录界面
        pass
    
    def post(self,req):
        #接收参数
        username = req.POST.get('username')
        password = req.POST.get('password')
        remembered = req.POST.get('remembered') #是否记住用户名
        
        if not all[username,password]:
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        #校验
        if not re.match(r'^[a-zA-Z0-9_-]{3,20}$',username):
            raise BusinessException(StatusCodeEnum.USER_ERR)
        
        
        #验证用户密码
        #对该方法进行了重写，可以用username和mobile进行登录
        user=authenticate(req,username=username,password=password)
        if user is None:
            #返回登录界面，用户名或密码错误
            pass
        #状态保持
        login(req,user)
        
        if remembered!='on':
            #若无需记住用户，浏览器会话结束session就过期
            req.session.set_expire(0)
        else:
            #记住用户，session一周后过期
            req.session.set_expire(60*60*24*7)
        
        
        #处理next参数（待定）
        
        #设置cookie 
        #response.set_cookie(CookieKey.USERNAME_KEY, user.username, max_age=constants.USERNAME_COOKIE_EXPIRES)
     
     
     # /users/logout    (unfinish)
class LogoutView(View):
    
    def get(self,req):
        logout(req)
        #重定向到登录界面且清除cookie
        #res=redirect()
        #res.delete_cookie()



     # /users/info   
class UserInfoView(LoginRequiredMixin,View):
     login_url='/users/login'
     permission_denied_message='未登录'
     
     def get(self,req):
         user_info={
             'username':req.user.username,
             'mobile':req.user.mobile,
             'email':req.user.email,
             'email_active':req.user.emal_active
         }
         
         #返回用户信息且跳转到用户中心
           


        
     # /users/emails       
class EmailView(View):
    
    def put(self,req):
        #修改邮箱
        json_req=json.loads(req.body.decode())
        email=json_req.get('email')
        
        if email is None:
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return BusinessException(StatusCodeEnum.EMAIL_ERR)
        
        req.user.email=email
        req.user.save()
        
        res=R.ok().data()
        
        #异步发送验证邮件
        verify_url=generate_verify_email_url(req.user)
        celery_send_verify_email(email,verify_url)
        
        return JsonResponse(res)
            
 
 # /users/emails/verification
class VerifyEmailView(View):
    
    def get(self,req):
        token=req.GET.get('token')
        if token is None:
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        user = check_verify_email_token(token)
        if user is None:
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
        
        try:
            user.email_active=True
            user.save()
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.SERVER_ERR)
        
        return redirect(reverse('users:info'))
            
        
            

    
    
               