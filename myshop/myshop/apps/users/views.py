import re
from django.conf import settings
from itsdangerous import json
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R
from myshop.utils.enums import StatusCodeEnum
from django.http import JsonResponse
from django.shortcuts import redirect, render,reverse
from django_redis import get_redis_connection
from .models import Address, User
from django.views import View
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from celery_tasks.email.task import celery_send_verify_email
from itsdangerous.jws import TimedJSONWebSignatureSerializer as Serializer
from myshop.utils.constants import USERNAME_COOKIE_EXPIRES, VERIFY_EMAIL_TOKEN_EXPIRES, CookieKey, Rediskey,USER_SESSION_EXPIRES
from myshop.utils.constants import HtmlTemplate,USER_ADDRESS_COUNT_LIMIT
import logging

logger=logging.getLogger(settings.LOGGER_NAME)


#生成邮箱验证url
def generate_verify_email_url(user):
    serializer=Serializer(settings.ITSDANGEROUS_SECRET_KEY,expires_in=VERIFY_EMAIL_TOKEN_EXPIRES)
    data={
        'user_id':user.id,
        'email':user.email
    }
    token=serializer.dumps(data).decode()
    verify_url=settings.EMAIL_VERIFY_URL+'?token='+token
    
    return verify_url
#检查邮箱验证token
def check_verify_email_token(token):
    serializer=Serializer(settings.ITSDANGEROUS_SECRET_KEY,expires_in=VERIFY_EMAIL_TOKEN_EXPIRES)
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

    # /users/namecounts/<username>
class UsernameCountView(View):
    
    def get(self,req,username):
        count=User.objects.filter(username=username).count()
        
        res=R.ok().data(**{
            'count':count
        })
        return JsonResponse(res)

    # /users/mobilecounts/<mobile>
class MobileCountView(View):
    
    def get(self,req,mobile):
        count=User.objects.filter(mobile=mobile).count()
        
        res=R.ok().data(**{
            'count':count
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
        return render(req,HtmlTemplate.REGISTER_HTML)
    
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
        
        if not re.match(r'^[a-zA-Z0-9_-]{3,20}$',self.username):
            raise BusinessException(StatusCodeEnum.USER_ERR)
        
        if not re.match(r'^[0-9A-Za-z]{8,20}$',self.password):
            raise BusinessException(StatusCodeEnum.PWD_ERR)       
        
        if not self.confirm_pwd==self.password:
            raise BusinessException(StatusCodeEnum.CPWD_ERR)
        
        if not re.match(r'^1(3\d|4[5-9]|5[0-35-9]|6[2567]|7[0-8]|8\d|9[0-35-9])\d{8}$',self.mobile):
            raise BusinessException(StatusCodeEnum.MOBILE_ERR)
        
        if self.allow!='on':
            raise BusinessException(StatusCodeEnum.ALLOW_ERR)
        
        
        
    def post(self,req):
        #信息检查
        self.verifi_parm(req)        
        redis_cli=get_redis_connection(alias=settings.VERIFY_CODE_CACHE_ALIAS)
        sms_code_key=Rediskey.SMS_CODE_KEY.format(mobile=self.mobile)
        sms_code_server=redis_cli.get(sms_code_key).decode()
        
        if not sms_code_server:
            return render(req,HtmlTemplate.REGISTER_HTML,{'sms_code_errmsg':'短信验证码无效'})
        
        if not sms_code_server.lower()==self.sms_code_client.lower():
            return render(req,HtmlTemplate.REGISTER_HTML,{'sms_code_errmsg':'短信验证码错误'})
        
        try:
            user=User.objects.create_user(
                username=self.username,
                password=self.password,
                mobile=self.mobile,
            )
        except Exception as e:
            logger.error(e)
            res=R.set_result(StatusCodeEnum.REGISTER_FAILED_ERR).data()
            return render(req,HtmlTemplate.REGISTER_HTML,res)
        
        return redirect(reverse('users:login'))
        
               
# /users/login
class LoginView(View):
    
    def get(self,req):
        #提供登录界面
        return render(req,HtmlTemplate.LOGIN_HTML)
    
    def post(self,req):
        #接收参数
        username = req.POST.get('username')
        password = req.POST.get('password')
        remembered = req.POST.get('remembered') #是否记住用户名
        
        
        if not all([username,password]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        #校验
        if not re.match(r'^[a-zA-Z0-9_-]{3,20}$',username):
            raise BusinessException(StatusCodeEnum.USER_ERR)
        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            raise BusinessException(StatusCodeEnum.USER_ERR)
        
        #验证用户密码
        user=authenticate(req,username=username,password=password)
        if user is None:
            #返回登录界面，用户名或密码错误
            return render(req, HtmlTemplate.LOGIN_HTML, {'account_errmsg': '用户名或密码错误'})
        #状态保持
        login(req,user)
        
        if remembered!='on':
            #若无需记住用户，浏览器会话结束session就过期
            req.session.set_expiry(0)
        else:
            #session信息保存时间,包括cookie和服务端session信息
            req.session.set_expiry(USER_SESSION_EXPIRES)
        
        redirect_url=req.GET.get('next')
        
        if redirect_url:
            res=redirect(redirect_url)
        else:
            res=redirect(reverse('contents:index'))
        #设置cookie 
        res.set_cookie(CookieKey.USERNAME_KEY, user.username, max_age=USERNAME_COOKIE_EXPIRES)

        return res
     
     # /users/logout  
class LogoutView(View):
    
    def get(self,req):
        logout(req)
        #重定向到登录界面且清除cookie
        res=redirect(reverse('users:login'))
        res.delete_cookie(CookieKey.USERNAME_KEY)
        
        return res


     # /users/info   
class UserInfoView(LoginRequiredMixin,View):
     
     def get(self,req):
         user_info={
             'username':req.user.username,
             'mobile':req.user.mobile,
             'email':req.user.email,
             'email_active':req.user.email_active
         }
         
         return render(req,HtmlTemplate.USER_CENTER_INFO_HTML,user_info)  

# /users/password
class UserPasswordView(View):
    
    def get(self,req):
        #跳转到修改密码页面
        return render(req,HtmlTemplate.USER_CENTER_PASS_HTML)
    
    def post(self,req):
        old_password=req.POST.get('old_password')
        new_password=req.POST.get('new_password')
        new_password2=req.POST.get('new_password2')
        
        if not all([old_password,new_password,new_password2]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        if not req.user.check_password(old_password):
            raise BusinessException(StatusCodeEnum.PWD_ERR)
        
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            raise BusinessException(StatusCodeEnum.NEW_PWD_ERR)
        
        if not new_password==new_password2:
            raise BusinessException(StatusCodeEnum.CPWD_ERR)       
        
        try:
            req.user.set_password(new_password)
            req.user.save()
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        logout(req)
        
        res=redirect(reverse('users:login'))
        res.delete_cookie(CookieKey.USERNAME_KEY)
        
        return res
      
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
            
# /users/addresses     
class AddressView(LoginRequiredMixin,View):
    #获取用户收货地址
    def get(self,req):
        addresses=Address.objects.filter(user=req.user,is_deleted=False)
        res_addresses_list=[]
        default_address_id=-1
        for address in addresses:
            address_dict={
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province_id": address.province.id,
                "city_id": address.city.id,
                "district_id": address.district.id,
                "province_name": address.province.name,
                "city_name": address.city.name,
                "district_name": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
        #默认地址总是第一个显示              
            if req.user.default_address and req.user.default_address.id==address.id:
                res_addresses_list.insert(0,address_dict)
                default_address_id=req.user.default_address.id
                
            else:
                res_addresses_list.append(address_dict)
        
        res={
            'default_address_id':default_address_id,
            'addresses':res_addresses_list
        }
        
        return render(req,HtmlTemplate.USER_CENTER_ADDRESS_HTML,res)
        
# /users/addresses/create/
class CreateAddressView(LoginRequiredMixin,View):
    
    def post(self,req):
        # 接收参数
        json_dict=json.loads(req.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        address_count=req.user.addresses.count()
        if address_count>=USER_ADDRESS_COUNT_LIMIT:
            res=R.set_result(StatusCodeEnum.ADDRESS_LIMIT_ERR).data()
            return JsonResponse(res)
            
            
        if not all([receiver,province_id,city_id,district_id,place,mobile]):
            logger.info(receiver,' ',province_id,' ',city_id,' ',district_id,' ',place,' ',mobile)
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        if not re.match(r'^1[0-9]{10}$',mobile):
            raise BusinessException(StatusCodeEnum.MOBILE_ERR)
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$',tel):
                raise BusinessException(StatusCodeEnum.TEL_ERR)
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                raise BusinessException(StatusCodeEnum.EMAIL_ERR)
        
        #创建地址对象并保存入库
        address=Address.objects.create(
            user=req.user,
            title=receiver,
            receiver=receiver,
            city_id=city_id,
            district_id=district_id,
            province_id=province_id,
            place=place,
            tel=tel,
            mobile=mobile,
            email=email
        )
        
        
        #返回该地址数据
        address_dict={
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province_id": address.province.id,
            "city_id": address.city.id,
            "district_id": address.district.id,
            "province_name": address.province.name,
            "city_name": address.city.name,
            "district_name": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        
        
        #如果无默认地址，则将其设为默认地址
        if req.user.default_address and req.user.default_address.is_deleted==False:
            res=R.ok().data(**{
                'address':address_dict,
            })
        else:
            req.user.default_address=address
            res=R.ok().data(**{
                'address':address_dict,
                'default_address_id':address.id
            })
        
        req.user.save()
        return JsonResponse(res)
        

# /users/addresses/<address_id>       
class UpdateOrDeleteAddressView(View):
    
    def put(self,req,address_id):
        
        json_dict=json.loads(req.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        
        if not all([receiver,province_id,city_id,district_id,place,mobile]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        if not re.match(r'^1[0-9]{10}$',mobile):
            raise BusinessException(StatusCodeEnum.MOBILE_ERR)
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$',tel):
                raise BusinessException(StatusCodeEnum.TEL_ERR)
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                raise BusinessException(StatusCodeEnum.EMAIL_ERR)
        
        try:
            address=Address.objects.get(id=address_id)
        except Exception as e:
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        address.user=req.user
        address.receiver=receiver
        address.province_id=province_id
        address.city_id=city_id
        address.district_id=district_id
        address.place=place
        address.mobile=mobile
        address.tel=tel
        address.email=email
        
        address.save()
        
        address_dict={
        "id": address_id,
        "receiver": receiver,
        "province_name": address.province.name,
        "city_name": address.city.name,
        "district_name": address.district.name,
        "place": address.place,
        "mobile": address.mobile,
        "tel": address.tel,
        "email": address.email,
        "province_id": address.province.id,
        "city_id": address.city.id,
        "district_id": address.district.id,
            }
        
        res=R.ok().data(**{
            'address':address_dict
        })
        
        return JsonResponse(res)
        
    def delete(self,req,address_id):
        try:
            address=Address.objects.filter(id=address_id)
            address.update(is_deleted=True)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        else:
            res=R.ok().data()
            return JsonResponse(res)
        
# /users/addresses/<address_id>/default
class DefaultAddressView(View):
    
    def put(self,req,address_id):
        try:
            address=Address.objects.get(id=address_id)
            req.user.default_address=address
            req.user.save()
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        else:
            res=R.ok().data()
            return JsonResponse(res)

# /users/addresses/<address_id>/title
class UpdateTitleAddressView(View):
    def put(self,req,address_id):
        json_dict=json.loads(req.body.decode())
        title=json_dict.get('title')
        try:
            address=Address.objects.get(id=address_id)
            address.title=title
            address.save()
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        else:
            res=R.ok().data()
            return JsonResponse(res)
        
        