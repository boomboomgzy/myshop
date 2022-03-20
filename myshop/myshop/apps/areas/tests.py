
from django.test import TestCase
from .models import Area
# Create your tests here.

list=Area.objects.filter(name='北京市')
new_list=[]
for province in list:
    new_list.append({
        'id':province.id,
        'name':province.name
    })
print(new_list)