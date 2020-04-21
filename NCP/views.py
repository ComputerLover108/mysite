from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from django.db.models import Q,Sum
import json
from datetime import date
from django.db import connection
from NCP.models import Global
import logging
# logger = logging.getLogger(__name__)
logger = logging.getLogger('django')

# Create your views here.
def overview(request):
    context = {'title':'新冠肺炎疫情'} 
    today = date.today()
    SQL = 'select max(update) from "global";'
    with connection.cursor() as cursor:
        cursor.execute(SQL)
        lastDay = cursor.fetchone()[0]
    # print('lastDay=%r:type=%r',lastDay,type(lastDay))
    # logger.info('lastDay=%r:type=%r',lastDay,type(lastDay))
    topCountry = Global.objects\
    .filter(update=lastDay)\
    .values_list('country','confirmation','totalconfirmation','cure','dead')\
    .order_by('-totalconfirmation')[:20]
    countries = []
    for x in topCountry:
        countries.append(x[0])
    # logger.info('%r',countries)
    col=["update",'sum("confirmation")']
    table = 'global'
    arg ="'"+"','".join(countries)+"'"
    # logger.info('arg=%r',arg)
    SQL = f'''
        select "update",sum("confirmation") from "{table}"
        where country not in ({arg}) 
        group by "{col[0]}"
        order by "{col[0]}";
    '''
    # logger.info('SQL=\n%r',SQL)
    with connection.cursor() as cursor:
        cursor.execute(SQL)
        others = cursor.fetchall()
        # logger.info('others=%r',others)        
    data = Global.objects\
        .filter(country__in=countries) \
        .values('update','country','confirmation')   
    context['topCountry'] = topCountry
    context['lastday'] = lastDay
    x = []
    temp = {}
    countries = Global.objects.distinct('country').values_list('country')
    dimensions = []
    a = []
    b = list(Global.objects\
        .distinct('update')\
        .filter(country='中国').values_list('update','confirmation'))
    
    count = Global.objects.filter(country='中国').count()
    for c in topCountry:
        name = c[0]
        temp[name] = list(Global.objects\
                    .filter(country=name).order_by('update').values_list('update','confirmation'))
        list2 = [0 for n in range(count-len(temp[name])) if count > len(temp[name])]
        temp[name] = [ x[1] for x in temp[name] ]
        temp[name] = list2+temp[name]
        temp[name].insert(0,name)        
        x.append(temp[name])
    dimensions = [x[0].isoformat() for x in b]
    dimensions.insert(0,'国家')
    # logger.info('dimensions length %r',len(dimensions))
    # logger.info('dimensions=%r',dimensions)
    # logger.info('others=%r',others)       
    context['dimensions'] = dimensions
    x.insert(0,dimensions)
    count1=len(x[0])
    count2=len(others)
    # logger.info('count1=%r,count2=%r',count1,count2)
    dimensions =[0]*(count1-count2) + [x[1] for x in others]
    dimensions.insert(0,'其他')
    # logger.info('dimensions=%r',dimensions)
    x.append(dimensions)
    context['data'] = x
    # logger.info('%r',x)
    return render(request,'NCP/overview.html',context)

def overall(request):
    data = Global.objects\
    .values('update',"continent","country","confirmation","totalconfirmation","suspect","cure","dead","remark", )\
    .filter(provinceName='')
    # data = Global.objects.filter(provinceName='')
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
        'NCP' : result
    }
    return JsonResponse(data,safe=False,json_dumps_params={'ensure_ascii':False})

def foreign(request):
    # SQL='''
    #     -- SELECT "update",sum("confirmation") FROM "NCP" WHERE "country" !='中国' GROUP BY "update" ORDER BY "update" ;
    #     SELECT "update",
    #            sum("confirmation") as "确诊",
    #            SUM("totalconfirmation") as "累计确诊", 
    #            SUM("dead") as "死亡", 
    #            SUM("cure") as "治愈"
    #     FROM "NCP"
    #     WHERE "country" !='中国'
    #     GROUP BY "update" 
    #     ORDER BY "update" ;        
    #     '''
    # with connection.cursor() as cursor:
    #     cursor.execute(SQL)
    #     data = cursor.fetchall()
   
    data = Global.objects\
        .filter(~Q(country='中国'))\
        .values('update')\
        .annotate(confirmation=Sum("confirmation"))\
        .order_by('update')
    data=list(data)
    # logger.info('type(data)=%r\n data=%r',type(data),data)        
    # data = {
    #     'NCP_foreign' : data
    # }
    return JsonResponse(data,safe=False,json_dumps_params={'ensure_ascii':False})

def confirmation(request,**args):
    SQL = '''

    '''

def totalconfirmation():
    pass

def suspect():
    pass    

def dead():
    pass

def cure():
    pass