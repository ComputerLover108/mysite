from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from datetime import date
from NCP.models import NovelCoronavirusPneumonia

# Create your views here.
def overview(request):
    context = {'title':'新冠肺炎疫情'} 
    # data = NovelCoronavirusPneumonia.objects.filter(provinceName='').values('update','countryName','currentConfirmedCount')
    # # print(type(data))
    # context['data'] = data
    # for x in data:
    #     print(x)
    today = date.today()
    topCountry = NovelCoronavirusPneumonia.objects.filter(provinceName='')\
    .filter(update=today)\
    .values_list('update','countryName','currentConfirmedCount','confirmedCount','suspectedCount','curedCount','deadCount')\
    .order_by('-currentConfirmedCount')[:10]
    countries = NovelCoronavirusPneumonia.objects.distinct('countryName').values_list('countryName')
    updates = NovelCoronavirusPneumonia.objects.distinct('update').values_list('update')
    # for x in topCountry:
    #     print(x[1])
    # print(type(topCountry))
    context['topCountry'] = topCountry
    context['updates'] = updates
    context['countries'] = countries
    return render(request,'NCP/overview.html',context)

def overall(request):
    data = NovelCoronavirusPneumonia.objects.values('update',"continentName","countryName","provinceName","cityName","currentConfirmedCount","confirmedCount","suspectedCount","curedCount","deadCount","comment", ).filter(provinceName='')
    # data = NovelCoronavirusPneumonia.objects.filter(provinceName='')
    for x in data:
        print(type(x))
        result=json.dumps(x)
        # print(type(result))
    # result=json.dumps(result)
    # return JsonResponse(result)
    return HttpResponse(content={'ok':0})