from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.result import R
from myshop.utils.exceptions import BusinessException
from .models import Area
from django.conf import settings
from django.core import cache
import logging

logger=logging.getLogger(settings.LOGGER_NAME)


# areas/
class AreasView(View):
    
    #提供地址数据
    def get(self,req):
        
        area_id=req.GET.get('area_id')
        
        
        
        # 表示请求area_id代表地址的子地址
        if area_id is not None:
            
                
            try:
                area=Area.objects.get(id=area_id)
            except Exception as e:
                logger.error(e)
                raise BusinessException(StatusCodeEnum.DB_ERR)           
            else:
                #格式化地址数据
                res_areas_list=[]
                sub_areas_list=area.sub_areas.all()
                for area_info in sub_areas_list:
                    res_areas_list.append({
                        'id':area_info.id,
                        'name':area_info.name
                    })
                
                res=R.ok().data(**{
                    'areas_list':res_areas_list
                })
                return JsonResponse(res)
        else:
            #无area_id 表示请求的是省级地址数据
            try:
                provinces_list=Area.objects.filter(parent=None)
            except Exception as e:
                logger.error(e)
                raise BusinessException(StatusCodeEnum.DB_ERR)           
            else:
                #格式化地址数据
                res_provinces_list=[]
                for province_info in provinces_list:
                    res_provinces_list.append({
                        'id':province_info.id,
                        'name':province_info.name
                    })
                
                res=R.ok().data(**{
                    'province_list':res_provinces_list
                })
                return JsonResponse(res)           