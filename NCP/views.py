from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from datetime import date
from django.db import connection
from NCP.models import NovelCoronavirusPneumonia
import logging
# logger = logging.getLogger(__name__)
logger = logging.getLogger('django')

# Create your views here.
def overview(request):
    context = {'title':'新冠肺炎疫情'} 
    # # print(type(data))
    # context['data'] = data
    # for x in data:
    #     print(x)
    today = date.today()
    SQL = 'select max(update) from "NCP";'
    # lastDay = NovelCoronavirusPneumonia.objects.raw(SQL)
    with connection.cursor() as cursor:
        cursor.execute(SQL)
        lastDay = cursor.fetchone()[0]
    # print('lastDay=%r:type=%r',lastDay,type(lastDay))
    logger.info('lastDay=%r:type=%r',lastDay,type(lastDay))
    topCountry = NovelCoronavirusPneumonia.objects.filter(provinceName='')\
    .filter(update=lastDay)\
    .values_list('update','countryName','currentConfirmedCount','confirmedCount','curedCount','deadCount')\
    .order_by('-currentConfirmedCount')[:20]
    countries = []
    for x in topCountry:
        countries.append(x[1])
    # logger.info('%r',countries)
    data = NovelCoronavirusPneumonia.objects.filter(provinceName='')\
        .filter(countryName__in=countries) \
        .values('update','countryName','currentConfirmedCount')   
    # countries = NovelCoronavirusPneumonia.objects.distinct('countryName').values_list('countryName')
    # updates = NovelCoronavirusPneumonia.objects.distinct('update').values_list('update')
    context['topCountry'] = topCountry
    # context['updates'] = updates
    # context['countries'] = countries
    # columnName = list(data[0].keys())
    # context['columnName'] = columnName
    x = []
    temp = {}
    # for row in data:
    #     temp['update'] = row['update'].isoformat()
    #     temp['countryName'] = row['countryName']
    #     temp['currentConfirmedCount'] = row['currentConfirmedCount']
    #     # logger.info('temp=%r',temp)
    #     x.append(temp)
    #     temp={}
    # context['data'] = x
    # logger.info('data=%r',x)
    countries = NovelCoronavirusPneumonia.objects.distinct('countryName').values_list('countryName')
    dimensions = []
    a = []
    b = list(NovelCoronavirusPneumonia.objects\
        .distinct('update')\
        .filter(countryName='中国').filter(provinceName='').values_list('update','currentConfirmedCount'))
    count = NovelCoronavirusPneumonia.objects.filter(countryName='中国').filter(provinceName='').count()
    # logger.info('type(count)=%r,count=%r',type(count),count)
    # logger.info('len(b)=%r:b=%r',len(b),b)
    # logger.info('dimensions=%r',dimensions)
    for c in topCountry:
        name = c[1]
        temp[name] = list(NovelCoronavirusPneumonia.objects.filter(provinceName='')\
                    .filter(countryName=name).order_by('update').values_list('update','currentConfirmedCount'))
        # logger.info('%r length %r value:%r',name,len(temp[name]),temp[name])
        list2 = [0 for n in range(count-len(temp[name])) if count > len(temp[name])]
        # logger.info('len=%r-%r:%r',count,len(temp[name]),list2)
        temp[name] = [ x[1] for x in temp[name] ]
        temp[name] = list2+temp[name]
        temp[name].insert(0,name)        
        x.append(temp[name])
    dimensions = [x[0].isoformat() for x in b]
    dimensions.insert(0,'国家')
    # logger.info('dimensions length %r',len(dimensions))        
    context['dimensions'] = dimensions
    x.insert(0,dimensions)
    context['data'] = x
    # logger.info('%r',x)
    return render(request,'NCP/overview.html',context)

def overall(request):
    data = NovelCoronavirusPneumonia.objects\
    .values('update',"continentName","countryName","provinceName","cityName","currentConfirmedCount","confirmedCount","suspectedCount","curedCount","deadCount","comment", )\
    .filter(provinceName='')
    # data = NovelCoronavirusPneumonia.objects.filter(provinceName='')
    result=[]
    for x in data:
        x['update'] = x['update'].isoformat()
        # logger.info('update type=%r value=%r',type(x['update']),x['update'])
        # logger.info('row=%r',x)
        result.append(x)
        # logger.info('result=%r\n',result)
    # data=json.dumps(result,ensure_ascii=False)
    # return HttpResponse(data,content_type="application/json")
    data = {
        'result' : result
    }
    return JsonResponse(data,safe=False,json_dumps_params={'ensure_ascii':False})
