from tabnanny import verbose
from tkinter.tix import MAX
from typing import OrderedDict
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    """自定义用户模型"""
    
    mobile=models.CharField(
        max_length=11,
        unique=True,
        verbose_name='手机号'
        )
    email_active=models.BooleanField(default=False,
                                     verbose_name='邮箱验证状态')
    
    class Meta:
        db_table='myshop_users'
        verbose_name='用户信息'
        verbose_name_plural=verbose_name
        ordering=['id']
        
    def __str__(self):
        return self.username
        