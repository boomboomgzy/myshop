from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.result import R
from myshop.utils.exceptions import BusinessException
from .models import Area
from django.conf import settings
from django.core.cache import cache
from myshop.utils.constants import Rediskey,MYSHOP_REDIS_AREAS_EXPIRES
import logging

logger=logging.getLogger(settings.LOGGER_NAME)

#格式化数据库的area_list
def format_area_list(area_list):
    res_area_list=[]
    for area in area_list:
        res_area_list.append({
            'id':area.id,
            'name':area.name
        })
    return res_area_list
    
# areas/
class AreasView(View):
    
    #提供地址数据
    def get(self,req):
        
        area_id=req.GET.get('area_id')
        
        # area_id为请求地址的id，为其返回该地址的子地址
        if area_id is not None:
            #先尝试获取缓存
            sub_areas_list=cache.get(Rediskey.SUB_AREAS_LIST_KEY.format(area_id=area_id))
            #缓存中没有再向数据库申请
            if sub_areas_list is None:
                try:
                    area=Area.objects.get(id=area_id)
                except Exception as e:
                    logger.error(e)
                    raise BusinessException(StatusCodeEnum.DB_ERR)           
                else:
                    #格式化地址数据
                    formatted_sub_areas_list=format_area_list(area.sub_areas.all())
                    #将其存入缓存 有效时间 单位:s
                    cache.set(Rediskey.SUB_AREAS_LIST_KEY.format(area_id=area_id),format_area_list,MYSHOP_REDIS_AREAS_EXPIRES)
                    
                    res=R.ok().data(**{
                        'areas_list':formatted_sub_areas_list
                    })
                    return JsonResponse(res)
            #缓存中有所需子地址的数据
            else:
                res=R.ok().data(**{
                    'areas_list':sub_areas_list
                })
                return 
        else:
            #无area_id 表示请求的是省级地址数据
            #先尝试从缓存中获取
            provinces_list=cache.get(Rediskey.PROVINCES_LIST_KEY)
            #缓存中没有则从数据库取
            if provinces_list is None:
                
                try:
                    provinces_list=Area.objects.filter(parent=None)
                except Exception as e:
                    logger.error(e)
                    raise BusinessException(StatusCodeEnum.DB_ERR)           
                else:
                    #格式化地址数据
                    formatted_provinces_list=format_area_list(provinces_list)
                    #存入缓存
                    cache.set(Rediskey.PROVINCES_LIST_KEY,formatted_provinces_list,MYSHOP_REDIS_AREAS_EXPIRES)              
                    res=R.ok().data(**{
                        'areas_list': formatted_provinces_list
                    })
                    return JsonResponse(res)           
            #缓存中有相应数据
            else:
                res=R.ok().data(**{
                        'areas_list': provinces_list
                    })
                return JsonResponse(res)   