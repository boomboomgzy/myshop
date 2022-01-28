"""
Django settings for myshop project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
from telnetlib import AUTHENTICATION

import itsdangerous
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# in gzy win BASE_DIR == G:\vscode\webprojec

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-44z+)qx3ybe*mqghf@1wjtffnmlme=72#4y_b=krp)2jj0sv)q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

#日志器名称
LOGGER_NAME='django'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器

    # 日志信息显示的格式
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },

    # 对日志进行过滤
    'filters': {
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },

    # 日志处理方法
    'handlers': {

        # 向终端中输出日志
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },

        # 向文件中输出日志
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',

            # 日志文件的位置
            'filename': os.path.join(BASE_DIR,'logs/myshop.log'),
            'encoding': 'utf-8',
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },

    # 日志器
    'loggers': {
        LOGGER_NAME: {  # 定义了一个名为django的日志器
            'handlers': ['file'],  # 只向文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
        
    #myshop     
    'myshop.apps.users',
    'myshop.apps.verifications',   
]

MIDDLEWARE = [
    #cors
    'corsheaders.middleware.CorsMiddleware',
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    #异常处理中间件
    'myshop.utils.middlewares.ExceptionMiddleware'
    
]

ROOT_URLCONF = 'myshop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    #    'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': BASE_DIR / 'db.sqlite3',
    #} 
        'default':{
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': '1',
        'NAME': 'myshop',
        }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/ShangHai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS=[os.path.join(BASE_DIR,'myshop','static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 缓存别名
DEFAULT_CACHE_ALIAS = 'default'
SESSION_CACHE_ALIAS = "session"
VERIFY_CODE_CACHE_ALIAS = 'verify_code'
HISTORY_CACHE_ALIAS = 'history'
CARTS_CACHE_ALIAS = 'carts'


#django-redis 配置

REDIS_URI='redis://127.0.0.1:6379'

CACHES = {
    DEFAULT_CACHE_ALIAS: {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "{REDIS_URI}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },    
    SESSION_CACHE_ALIAS: {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "{REDIS_URI}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    VERIFY_CODE_CACHE_ALIAS: {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "{REDIS_URI}/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
    
    
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

#替换内置user
AUTH_USER_MODEL='users.User'

#CORS 白名单

CORS_ALLOWED_ORIGINS=(
    'http://127.0.0.1:8000',
    'http://localhost:8000',
)

#允许携带cookie
CORS_ALLOW_CREDENTIALS = True

#CORS_ORIGIN_ALLOW_ALL = True

AUTHENTICATION_BACKENDS=['myshop.utils.backend.UserNameAndEmailBackend'] 

#未登录用户的默认跳转路由 
LOGIN_URL = '/users/login' 
  
#邮箱配置
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_FROM='myshop<3228352301@qq.com>'
EMAIL_HOST='smtp.qq.com'
EMAIL_PORT='465'
EMAIL_HOST_USER='3228352301@qq.com'
EMAIL_HOST_PASSWORD='huangjing.1314'
# 邮箱验证链接
EMAIL_VERIFY_URL = 'http://127.0.0.1:8000/emails/verification/'


#itsdangerous密钥
ITSDANGEROUS_SECRET_KEY='367ee6cfd1704c0b786d3407b130c8f7'
