from itertools import count
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R
from myshop.utils.enums import StatusCodeEnum
from django.http import JsonResponse
from django.shortcuts import render
from .models import User
from django.views import View
# Create your views here.


class UsernameCountView(View):
    
    # /users/usernamecounts/<str:username>
    def get(self,req,check_username):
        #username检查
        count=User.objects.filter(username=check_username).count()
        
        res=R.ok().data(**{
            'username_count':count
        })
        return JsonResponse(res)
        
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
        
    # /users/register
    def post(self,req):
        #信息检查
        self.verifi_parm(req)        

    
            