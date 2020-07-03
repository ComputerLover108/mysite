import requests
import json
import time
import datetime
import threading
import os
import psycopg2
import csv
import logging
import argparse
import random
import re
from bs4 import BeautifulSoup
# from requests.exceptions import ReadTimeout,HTTPError,RequestException
import multiprocessing

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler('ncp.log')
handler.setLevel(logging.INFO)
formatter = "%(message)s %(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d "
formatter = logging.Formatter(formatter)
handler.setFormatter(formatter)
logger.addHandler(handler)
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# logger.addHandler(console)

user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.4150.1 Iron Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36 Maxthon/5.3.8.2000',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.9) Gecko/20100101 Goanna/4.4 Firefox/68.9 PaleMoon/28.8.4'
]
# headers = {'User-Agent': random.choice(user_agent_list)}
nameMap = dict()

class MyPostgreSQL:
    def __init__(self,dbname,user,password,host,port):
        self.dbname=dbname
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.conn = psycopg2.connect(database=self.dbname,user=self.user,password=self.password,host=self.host,port=self.port)
        self.cursor = self.conn.cursor()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cursor.close()
        self.conn.close()

    def connect(self,dbname,user,password,host,port):
        self.conn = psycopg2.connect(dbname,user,password,host,port)
        self.cursor = conn.cursor()
    
    def execute(self,SQL,**args):
        try:
            if args:
                self.cursor.execute(SQL,args)
            else:
                self.cursor.execute(SQL)
        except Exception as e:
            logger.info(e)
            self.conn.rollback()
            self.cursor.execute(SQL)
        self.conn.commit()

# https://lab.isaaclin.cn/nCoV/api
# 疫情数据处理，并存入数据库中
def NCP_save(records,**extra):
    rows=[]
    global_rows=[]
    country_rows=[]
    province_rows=[]
    for record in records:       
        row = []
        citys = []
        if "updateTime" in record:
            dt = record["updateTime"]
            # logger.info('type(dt)=%r,dt=%r',type(dt),dt)
            # logger.info('%r\n',record)
            if isinstance(dt,int):
                d = datetime.datetime.fromtimestamp(dt/1000.0,tz=None)
            elif isinstance(dt,int):
                d = datetime.datetime.fromisoformat(dt)
            else:
                # logger.info('时间处理失败！')
                continue
            sd = d.strftime("%Y-%m-%d")
            updateTime = sd
            continentName = record["continentName"] if "continentName" in record else None
            countryName = record["countryName"] if "countryName" in record else None
            provinceName = record["provinceName"] if "provinceName" in record else None
            cityName = record["cityName"] if "cityName" in record else None
            comment = record['comment'] if "comment" in record else None

            if "continentName" in record and "continentEnglishName" in record:
                nameMap[continentName] = record["continentEnglishName"]
            if "countryName" in record and "countryEnglishName" in record:
                nameMap[countryName] = record["countryEnglishName"]
            if "cityName" in record and "cityEnglishName" in record:
                nameMap[cityName] = record["cityEnglishName"] 

            continentName = continentName if continentName else ''
            countryName = countryName if countryName != continentName else '' 
            provinceName = provinceName if provinceName != countryName else ''
            cityName = cityName if cityName else ''
            # china_json 数据处理
            if extra:
                continentName = extra['continentName']
                countryName = extra['countryName']
            if "generalRemark" in record:
                comment = record['generalRemark']            
            comment = comment if comment else ''
           
            currentConfirmedCount = record["currentConfirmedCount"] if "currentConfirmedCount" in record else None
            confirmedCount = record["confirmedCount"] if "confirmedCount" in record else None
            suspectedCount = record["suspectedCount"] if "suspectedCount" in record else None
            curedCount = record["curedCount"] if "curedCount" in record else None
            deadCount = record["deadCount"] if "deadCount" in record else None

            currentConfirmedCount = currentConfirmedCount if isinstance(currentConfirmedCount,int) else 0
            confirmedCount = confirmedCount if isinstance(confirmedCount,int) else 0
            suspectedCount = suspectedCount if isinstance(suspectedCount,int) else 0
            curedCount = curedCount if isinstance(curedCount,int) else 0
            deadCount = deadCount if isinstance(deadCount,int) else 0
            # 2月9日以前没有当前确诊记录，只有确诊记录。
            # logger.info('%r<%r=%r',d,datetime.datetime(2020,2,9),d<datetime.datetime(2020,2,9))
            if d <= datetime.datetime(2020,2,9,0,0):
                # logger.info('update=%r,currentConfirmedCount=%r,confirmedCount=%r,suspectedCount=%r,curedCount=%r,deadCount=%r',d,currentConfirmedCount,confirmedCount,suspectedCount,curedCount,deadCount)                
                currentConfirmedCount = confirmedCount if currentConfirmedCount==0 else currentConfirmedCount

            row.append(updateTime)
            row.append(continentName)   
            row.append(countryName)
            row.append(provinceName)
            row.append(cityName)
            row.append(currentConfirmedCount)
            row.append(confirmedCount)
            row.append(suspectedCount)
            row.append(curedCount)
            row.append(deadCount)
            row.append(comment)
            global_row = [updateTime,continentName,countryName,currentConfirmedCount,confirmedCount,suspectedCount,curedCount,deadCount,comment]
            # logger.info(global_row)
            global_rows.append(global_row)            
            if 'cities' in record:
                citys = record['cities']
                # logger.info('citysTable={}'.format(citys))
                if citys:                            
                    for city in citys:
                        # logger.info('city={}'.format(city))
                        cityRow=[]
                        if 'cityName' in city:
                            cityName = city['cityName'] 
                        else:
                            continue 
                        currentConfirmedCount = city["currentConfirmedCount"] if "currentConfirmedCount" in city else None
                        confirmedCount = city["confirmedCount"] if "confirmedCount" in city else None
                        suspectedCount = city["suspectedCount"] if "suspectedCount" in city else None
                        curedCount = city["curedCount"] if "curedCount" in city else None
                        deadCount = city["deadCount"] if "deadCount" in city else None

                        comment = city['comment'] if "comment" in city else None
                        comment = comment if comment else ''

                        currentConfirmedCount = currentConfirmedCount if isinstance(currentConfirmedCount,int) else 0
                        confirmedCount = confirmedCount if isinstance(confirmedCount,int) else 0
                        suspectedCount = suspectedCount if isinstance(suspectedCount,int) else 0
                        curedCount = curedCount if isinstance(curedCount,int) else 0
                        deadCount = deadCount if isinstance(deadCount,int) else 0
                        if d <= datetime.datetime(2020,2,9,0,0):
                            # logger.info('update=%r,currentConfirmedCount=%r,confirmedCount=%r,suspectedCount=%r,curedCount=%r,deadCount=%r',d,currentConfirmedCount,confirmedCount,suspectedCount,curedCount,deadCount)
                            currentConfirmedCount = confirmedCount if currentConfirmedCount==0 else currentConfirmedCount

                        cityRow.append(sd)
                        cityRow.append(continentName)
                        cityRow.append(countryName)
                        cityRow.append(provinceName)                            
                        cityRow.append(cityName)
                        cityRow.append(currentConfirmedCount)
                        cityRow.append(confirmedCount)
                        cityRow.append(suspectedCount)
                        cityRow.append(curedCount)
                        cityRow.append(deadCount)
                        cityRow.append(comment)
                        if cityName:
                            province_row = [sd,countryName,provinceName,cityName,currentConfirmedCount,confirmedCount,suspectedCount,curedCount,deadCount,comment]
                            province_rows.append(province_row)
                            # logger.info(province_row)
                        else:
                            country_row = [sd,countryName,provinceName,currentConfirmedCount,confirmedCount,suspectedCount,curedCount,deadCount,comment]
                            country_rows.append(country_row)
                            # logger.info(country_row)
                        # logger.info('cityRow={}'.format(cityRow))
                        if cityRow:
                            rows.append(cityRow)
                else:
                    cityName = None                                            
        else:
            continue     
        if row:
            rows.append(row)
    logger.info('NCP global records counts %r',len(global_rows))
    logger.info('NCP country records counts %r',len(country_rows))
    logger.info('NCP province records count %r',len(province_rows))
    logger.info('NCP records count %r',len(rows))
    # logger.info('nameMap = %r',nameMap)
    # filename = 'nameMap.json'
    # with open(filename,'w') as f:
    #     json.dump(nameMap,f,ensure_ascii=False,indent=4,sort_keys=True)    
    if global_rows:
        name = 'global'
        columns = ["update","continent","country","confirmation","totalConfirmation","suspect","cure","dead","remark"]
        coreColumns = ["confirmation","totalConfirmation","suspect","cure","dead","remark"]
        data={
            'table':name,
            'columns':columns,
            'coreColumns':coreColumns,
            'rows':global_rows
        }
        save(data)
    if country_rows:
        name = 'global'
        columns = ["update","country","province","confirmation","totalConfirmation","suspect","cure","dead","remark"]
        coreColumns = ["confirmation","totalConfirmation","suspect","cure","dead","remark"]
        data={
            'table':name,
            'columns':columns,
            'coreColumns':coreColumns,
            'rows':country_rows
        }
        save(data)        
    if province_rows:
        name = 'province'
        columns = ["update","country","province","city","confirmation","totalConfirmation","suspect","cure","dead","remark"]
        coreColumns = ["confirmation","totalConfirmation","suspect","cure","dead","remark"]
        data={
            'table':name,
            'columns':columns,
            'coreColumns':coreColumns,
            'rows':province_rows
        }
        save(data)        
    # psql.cursor.copy_from(f, "NCP",columns=fieldnames,sep=',', null='\\N', size=16384)
    # filename = 'NCP.csv'
    # with open(filename, 'w', newline='') as csvfile:
    #     fieldnames = records[0].keys()
    #     logger.info(fieldnames)
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     writer.writerows(records)
    # psql.cursor.copy_from(csvfile, 'ncp',columns=fieldnames,sep=',', size=16384) 

# 数据存入数据库
def save(record):
    table = record['table']
    columns = record['columns'] 
    coreColumns = record['coreColumns']
    rows = record['rows']
    SQL_snippet =f'ON CONFLICT ON CONSTRAINT "{table}_unique" DO UPDATE SET '
    for col in coreColumns:
       SQL_snippet += f' "{col}" = EXCLUDED."{col}",'
    SQL = f"""insert into "{table}" ("{'","'.join(columns)}") values ({','.join(['%s'] * len(columns))}) """
    SQL_snippet = SQL_snippet.rstrip(',')+';'
    SQL += SQL_snippet
    # logger.info('sql in save,sql:\n%r',SQL)    
    dbname = 'COVID-19'
    user='operator'
    password='5302469'
    # host='localhost'
    host='127.0.0.1'
    port='2012'
    psql = MyPostgreSQL(dbname=dbname,user=user,password=password,host=host,port=port)    
    psql.cursor.executemany(SQL,rows)
    psql.conn.commit()    

# json数据存入json文件
def save_to_file(file,data):
    # json_str = json.dumps(data, indent=4)
    with open(file, 'w') as json_file:
        json_file.write(data)

# 全球疫情信息分析
def json_NCP_world(data):
    records = data["results"]
    NCP_save(records)

# 全国疫情概览
def json_NCP_China(data):
    records = data["results"]
    extra = {'continentName':'亚洲','countryName':'中国'}
    NCP_save(records,**extra)

# 新冠新闻
def json_NCP_news(data):
    records = data["results"]
    # 从指定json文件中提取数据
    # filename = "news.json"
    # with open(filename, 'r') as f:
    #     data = json.load(f)
    #     records = data         
    logger.info("news records count %r",len(records))
    # logger.info("news:\n%r",json_reads)
    rows = []
    for record in records:
        row=[]
        title = record["title"]
        summary = record["summary"]
        infoSource = record["infoSource"]
        sourceUrl = record["sourceUrl"]
        if "pubDate" in record:
            dt = record["pubDate"]
            if isinstance(dt,str):
                d = datetime.datetime.fromtimestamp(int(dt)/1000.0,tz=None)
                # logger.info("d = %r",d)
            elif isinstance(dt,int):
                d = datetime.datetime.fromtimestamp(dt/1000.0,tz=None)
            # elif isinstance(dt,int):
            #     d = datetime.datetime.fromisoformat(int(dt))
                # logger.info("d = %r",d)
            else:
                logger.info("record failure %r",record)
                continue
            sd = d.strftime("%Y-%m-%d")                
        # else:
        #     sd = datetime.date.today()
        update = sd
        row = [update,title,summary,infoSource,sourceUrl]
        rows.append(row)
        # logger.info("news:%r,%r,%r,%r",update,title,summary,content)
    name = 'news'
    columns = ["update","title","summary","infoSource","sourceUrl"]
    coreColumns = ["update","title"]
    data={
        'table':name,
        'columns':columns,
        'coreColumns':coreColumns,
        'rows':rows
    }
    save(data)

# 新冠谣言
def json_NCP_rumors(data):
    records = data["results"]
    # 从指定json文件中提取数据
    # filename = "rumors.json"
    # with open(filename, 'r') as f:
    #     data = json.load(f)
    #     records = data         
    logger.info("rumors records count %r",len(records))
    # logger.info("rumors:\n%r",json_reads)
    rows = []
    for record in records:
        row=[]
        title = record["title"]
        summary = record["mainSummary"]
        content = record["body"]
        if "crawlTime" in record:
            dt = record["crawlTime"]
            # logger.info('type(dt)=%r,dt=%r',type(dt),dt)
            # logger.info('%r\n',record)
            if isinstance(dt,int):
                d = datetime.datetime.fromtimestamp(dt/1000.0,tz=None)
            elif isinstance(dt,int):
                d = datetime.datetime.fromisoformat(dt)
            sd = d.strftime("%Y-%m-%d")                
        else:
            sd = datetime.date.today()
        update = sd
        row = [update,title,summary,content]
        rows.append(row)
        # logger.info("rumors:%r,%r,%r,%r",update,title,summary,content)
    name = 'rumors'
    columns = ["update","title","summary","content"]
    coreColumns = ["update","title"]
    data={
        'table':name,
        'columns':columns,
        'coreColumns':coreColumns,
        'rows':rows
    }
    save(data)
    # filename = 'rumors1.json'
    # with open(filename,'w') as f:
    #     json.dump(records,f,ensure_ascii=False,indent=4,sort_keys=True) 

# QQ新冠全国疫情
def json_NCP_QQ_disease(data):
    json_data = json.loads(data)
    globalSummaryRecords=[]
    totoalProvinceRecords=[]
    totalCityRecords=[]     
    rows = []
    records = json_data['areaTree']
    for record in records:
        update = datetime.date.fromtimestamp(time.time()).isoformat()
        continent = '亚洲'
        country = '中国'
        remark = ''
        confirmation=record['total']['nowConfirm']
        totalConfirmation=record['total']['confirm']
        suspect = record['total']['suspect']
        cure = record['total']['heal']
        dead = record['total']['dead']
        row=[update,continent,country,confirmation,totalConfirmation,suspect,cure,dead,remark]
        # logger.info('china row=%r',row)
        rows.append(row)
        if 'children' in record:
            provinceRecords = record['children']
            for x in provinceRecords:
                provinceRecord={}
                provinceRecord['update'] = update
                provinceRecord['country'] = country
                provinceRecord['province'] = x['name']
                provinceRecord['confirmation']=x['total']['nowConfirm']
                provinceRecord['totalConfirmation']=x['total']['confirm']
                provinceRecord['suspect'] = x['total']['suspect']
                provinceRecord['cure'] = x['total']['heal']
                provinceRecord['dead'] = x['total']['dead']
                provinceRecord['remark'] = ''
                totoalProvinceRecords.append(provinceRecord)
                province = provinceRecord['province']
                if 'children' in x:
                    cityRecords = x['children']
                    for xx in cityRecords:
                        cityRecord={}
                        cityRecord['update'] = update
                        cityRecord['country'] = country
                        cityRecord['province'] = province
                        cityRecord['city'] = xx['name']
                        cityRecord['confirmation']=xx['total']['nowConfirm']
                        cityRecord['totalConfirmation']=xx['total']['confirm']
                        cityRecord['suspect'] = xx['total']['suspect']
                        cityRecord['cure'] = xx['total']['heal']
                        cityRecord['dead'] = xx['total']['dead']
                        cityRecord['remark'] = ''
                        totalCityRecords.append(cityRecord)                                                             
                        # logger.info('confirmation=%r',cityRecord['confirmation'])
                        # logger.info('xx[total][nowConfirm]=%r',xx['total']['nowConfirm'])
   
    # 省或州等一级单位新冠疫情数据
    for record in totoalProvinceRecords:
        row=[]
        record['confirmation'] = record['confirmation'] if 'confirmation' in record else 0
        record['suspect'] = record['suspect'] if 'suspect' in record else 0
        row.append(record['update'])
        row.append(record['country'])
        row.append(record['province'])
        row.append(record['confirmation'])
        row.append(record['totalConfirmation'])
        row.append(record['suspect'])
        row.append(record['cure'])
        row.append(record['dead'])
        row.append(record['remark'])
        rows.append(row)
    name = "country"
    constraint='country_unique'
    columns = ["update","country","province","confirmation","totalConfirmation","suspect","cure","dead","remark"]
    coreColumns = ["confirmation","totalConfirmation","suspect","cure","dead","remark"]
    data={
        'table':name,
        'columns':columns,
        'coreColumns':coreColumns,
        'rows':rows
    }
    save(data)
    logger.info('China totoalProvinceRecords 共有%r条记录。',len(totoalProvinceRecords))

    # 城市，二级单位新冠疫情数据
    rows=[]    
    for record in totalCityRecords:
        row=[]
        record['confirmation'] = record['confirmation'] if 'confirmation' in record else 0
        record['suspect'] = record['suspect'] if 'suspect' in record else 0
        record['totalConfirmation'] = record['totalConfirmation'] if 'totalConfirmation' in record else 0
        row.append(record['update'])
        row.append(record['country'])
        row.append(record['province'])
        row.append(record['city'])
        row.append(record['confirmation'])
        row.append(record['totalConfirmation'])
        row.append(record['suspect'])
        row.append(record['cure'])
        row.append(record['dead'])
        row.append(record['remark'])
        rows.append(row)
        # logger.info('cityRecord=%r',record)
    name = "province"
    constraint='province_unique'
    columns = ["update","country","province","city","confirmation","totalConfirmation","suspect","cure","dead","remark"]
    coreColumns = ["confirmation","totalConfirmation","suspect","cure","dead","remark"]
    data={
        'table':name,
        'columns':columns,
        'coreColumns':coreColumns,
        'rows':rows
    }
    save(data)
    logger.info('China totalCityRecords 共有%r条记录。',len(totalCityRecords))
    
# QQ新冠全国疫情历史数据
def json_NCP_QQ_disease_other(data):
    json_data = json.loads(data)
    rows =[]
    records = json_data['chinaDayList']
    for record in records:
        continent = '亚洲'
        country = '中国'
        remark = '' 
        temp=record['date'].split('.')
        sd = '2020-'+temp[0]+'-'+temp[1]
        update = datetime.date.fromisoformat(sd).isoformat()
        confirmation=record['nowConfirm']
        totalConfirmation=record['confirm']
        suspect = record['suspect']
        cure = record['heal']
        dead = record['dead']
        row=[update,continent,country,confirmation,totalConfirmation,suspect,cure,dead,remark]
        rows.append(row)
        # logger.info('%r\n',row)

    name = 'global'
    columns = ["update","continent","country","confirmation","totalConfirmation","suspect","cure","dead","remark"]
    coreColumns = ["confirmation","totalConfirmation","suspect","cure","dead","remark"]
    data={
        'table':name,
        'columns':columns,
        'coreColumns':coreColumns,
        'rows':rows
    }
    save(data)
    logger.info('China total records 共有%r条记录。',len(rows))    

# QQ新冠全球疫情
def json_NCP_QQ_disease_foreign(data):
    globalSummaryRecords=[]
    totoalProvinceRecords=[]   
    rows = []
    json_data = json.loads(data)
    records = json_data['foreignList']
    # logger.info('json_NCP_QQ_disease_foreign:\n %r',records)
    for record in records:
        remark = ''
        temp=record['date'].split('.')
        sd = '2020-'+temp[0]+'-'+temp[1]
        update = datetime.date.fromisoformat(sd).isoformat()
        continent = record['continent']            
        country = record['name']
        confirmation=record['nowConfirm']
        totalConfirmation=record['confirm']
        suspect = record['suspect']
        cure = record['heal']
        dead = record['dead']
        row=[update,continent,country,confirmation,totalConfirmation,suspect,cure,dead,remark]
        if 'children' in record:
            provinceRecords = record['children']
            for record in provinceRecords:
                temp=record['date'].split('.')
                sd = '2020-'+temp[0]+'-'+temp[1]                
                record['remark'] = ''
                record['country'] = country
                record['province'] = record.pop('name')
                record['update'] = datetime.date.fromisoformat(sd).isoformat()
                # record['confirmation']=record.pop('nowConfirm')
                record['totalConfirmation']=record.pop('confirm')
                record['cure'] = record.pop('heal')
                totoalProvinceRecords.append(record)                  
        rows.append(row)

    name = 'global'
    columns = ["update","continent","country","confirmation","totalConfirmation","suspect","cure","dead","remark"]
    coreColumns = ["confirmation","totalConfirmation","suspect","cure","dead","remark"]
    data={
        'table':name,
        'columns':columns,
        'coreColumns':coreColumns,
        'rows':rows
    }
    save(data)
    logger.info('global records 共有%r条记录。',len(rows))

    # 省或州等一级单位新冠疫情数据
    for record in totoalProvinceRecords:
        row=[]
        record['confirmation'] = record['confirmation'] if 'confirmation' in record else 0
        record['suspect'] = record['suspect'] if 'suspect' in record else 0
        row.append(record['update'])
        row.append(record['country'])
        row.append(record['province'])
        row.append(record['confirmation'])
        row.append(record['totalConfirmation'])
        row.append(record['suspect'])
        row.append(record['cure'])
        row.append(record['dead'])
        row.append(record['remark'])
        rows.append(row)
    name = "country"
    constraint='country_unique'
    columns = ["update","country","province","confirmation","totalConfirmation","suspect","cure","dead","remark"]
    coreColumns = ["confirmation","totalConfirmation","suspect","cure","dead","remark"]
    data={
        'table':name,
        'columns':columns,
        'coreColumns':coreColumns,
        'rows':rows
    }
    save(data)
    logger.info('global totoalProvinceRecords 共有%r条记录。',len(totoalProvinceRecords))

    # 各国新冠历史数据
    rows = []
    records = json_data['globalDailyHistory']               
    for record in records:
        if record['date'].count('.')==1:
            year = '2020'
            month,day = record['date'].split('.')
        elif record['date'].count('.')==2:
            year,month,day=record['date'].split('.')
        else:
            msg='{}不是有效的日期格式！'.format(record['date'])
            logger.error(msg)
            continue
        update = datetime.date(int(year),int(month),int(day))
        confirm=record['all']['confirm']
        cure = record['all']['heal']
        dead = record['all']['dead']
        deadRate=record['all']['deadRate']            
        cureRate=record['all']['healRate']
        row=[update,confirm,cure,dead,cureRate,deadRate]
        rows.append(row)
        # logger.info('globalDailyHistory:\n %r',row)

    name = 'globalSummary'
    columns = ["update","confirm","cure","dead","cureRate","deadRate"]
    coreColumns = ["confirm","cure","dead","cureRate","deadRate"]
    data={
        'table':name,
        'columns':columns,
        'coreColumns':coreColumns,
        'rows':rows
    }
    save(data)
    logger.info('globalSummaryRecords 共有%r条记录。',len(rows))

# https://lab.isaaclin.cn/nCoV/api 网站新冠疫情数据爬取
def crawl_NCP():
    try:
        headers = {'User-Agent': random.choice(user_agent_list)}
        timeout = (9,60)

        # 全球疫情信息
        url = "https://lab.isaaclin.cn/nCoV/api/area"
        response = requests.get(url,headers=headers,timeout=timeout)
        response.raise_for_status()
        data = response.json()
        json_NCP_world(data)


        # 全国疫情概览
        url = "https://lab.isaaclin.cn/nCoV/api/overall"
        response = requests.get(url,headers=headers,timeout=timeout)
        response.raise_for_status()
        data = response.json()
        json_NCP_China(data)


        # 爬取谣言
        url = "https://lab.isaaclin.cn/nCoV/api/rumors"
        params = {"page" : "1","num" : "100"}
        response = requests.get(url,headers=headers,params=params,timeout=timeout)
        response.raise_for_status()
        data = response.json()
        json_NCP_rumors(data)


        # 爬取新冠新闻
        url = "https://lab.isaaclin.cn/nCoV/api/news"
        params = {"page" : "1","num" : "100"}
        response = requests.get(url,headers=headers,params=params,timeout=timeout)
        response.raise_for_status()
        data = response.json()
        json_NCP_news(data)
 
    except Exception as e:
        msg = 'crawl_NCP failure：{}'.format(e)
        logger.error(msg)

def crawl_NCP_dingxiang(url,timeout):
    response = requests.get(url,headers=headers,timeout=timeout)
    msg = 'response.status_code={}'.format(response.status_code)
    # logger.info('msg=%r content=%r',msg,response.content) 
    soup = BeautifulSoup(response.content, 'lxml')

    overall_information = re.search(r'(\{"id".*\}\})\}', str(soup.find('script', attrs={'id': 'getStatisticsService'})))
    logger.info('overall_information=%r',overall_information)
    # if overall_information:
    #     self.overall_parser(overall_information=overall_information)

    area_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getAreaStat'})))
    # if area_information:
    #     self.area_parser(area_information=area_information)

    abroad_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getListByCountryTypeService2true'})))
    # if abroad_information:
    #     self.abroad_parser(abroad_information=abroad_information)

    news_chinese = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getTimelineServiceundefined'})))
    # if news_chinese:
    #     self.news_parser(news=news_chinese)

    news_english = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getTimelineService2'})))
    # if news_english:
    #     self.news_parser(news=news_english)

    rumors = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getIndexRumorList'})))
    # if rumors:
    #     self.rumor_parser(rumors=rumors)       

def crawl_NCP_qq():
    # 腾讯数据接口
    # https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5
    # https://view.inews.qq.com/g2/getOnsInfo?name=disease_other
    # https://view.inews.qq.com/g2/getOnsInfo?name=disease_foreign  
 
    try:      
        url='https://view.inews.qq.com/g2/getOnsInfo'
        headers = {'User-Agent': random.choice(user_agent_list)}
        timeout = (9,60)
        params = {}

        # 中国各省市当日实时数据
        params['name'] = 'disease_h5'        
        response = requests.get(url,headers=headers,params=params,timeout=timeout)
        response.raise_for_status()
        result = response.json()
        china_json =result['data']

        # 中国历史数据及每日新增数据
        params['name']='disease_other'
        response = requests.get(url,headers=headers,params=params,timeout=timeout)
        response.raise_for_status()
        result = response.json()
        other_json = result['data']

        # 全球实时数据及历史数据、中国输入病例
        params['name'] = 'disease_foreign'
        response = requests.get(url,headers=headers,params=params,timeout=timeout)
        response.raise_for_status()
        result = response.json()
        foreign_json = result['data']
        # logger.info('%r',foreign_json)
        
        # fileName = "NCP_QQ_disease_h5.json"
        # save_to_file(fileName,china_json)
        # fileName = "NCP_QQ_disease_other.json"
        # save_to_file(fileName,other_json)
        # fileName = "NCP_QQ_disease_foreign.json"
        # save_to_file(fileName,foreign_json)
        # 并行存入文件
        ps1 = multiprocessing.Process(target=save_to_file,args=('NCP_QQ_disease_h5.json',china_json))
        ps2 = multiprocessing.Process(target=save_to_file,args=('NCP_QQ_disease_other.json',other_json))
        ps3 = multiprocessing.Process(target=save_to_file,args=('NCP_QQ_disease_foreign.json',foreign_json))

        ps1.start()
        ps2.start()
        ps3.start()
        # json_NCP_QQ_disease(china_json)
        # json_NCP_QQ_disease_other(other_json)
        # json_NCP_QQ_disease_foreign(foreign_json)
        # 并行处理，并存入数据库        
        p1 = multiprocessing.Process(target=json_NCP_QQ_disease,args=(china_json,))
        p2 = multiprocessing.Process(target=json_NCP_QQ_disease_other,args=(other_json,))
        p3 = multiprocessing.Process(target=json_NCP_QQ_disease_foreign,args=(foreign_json,))

        p1.start()
        p2.start()
        p3.start()

        

    except Exception as e:
        logger.error('crawl_NCP_qq failure: %r',e)              


def DXY_csv_to_database(filename):
    # logger.info("filename is %r",filename)
    with open(filename, newline='', encoding='UTF-8-sig') as csvfile:
        # spamreader = csv.reader(csvfile)
        # dialect = csv.Sniffer().sniff(csvfile.read(1024))
        # csvfile.seek(0)
        # reader = csv.reader(csvfile, dialect)        
        reader = csv.DictReader(csvfile)
        # logger.info('records=%r',type(reader))
        records=[]
        cityRow=[]
        provinceRow=[]
        rows=[]
        for row in reader:
            records.append(row)
            # logger.info(row)
        # logger.info('type(records)=%r type(records[0])=%r',type(records),type(records[0]))
        # logger.info('type(records)=%r,len(records)=%r',type(records),len(records))
        # DBSave(records)
        for record in records:
            if "updateTime" in record:
                dt = record["updateTime"]
                # logger.info('%r\n',record)
                if isinstance(dt,int):
                    d = datetime.datetime.fromtimestamp(dt/1000.0,tz=None)
                elif isinstance(dt,str):
                    d = datetime.datetime.fromisoformat(dt)
                else:
                    continue
                # if d < datetime.datetime(2020,3,1,0,0):
                #     continue
                sd = d.strftime("%Y-%m-%d")
                updateTime = sd
                continentName = record["continentName"] if "continentName" in record else None
                countryName = record["countryName"] if "countryName" in record else None
                provinceName = record["provinceName"] if "provinceName" in record else None
                cityName = record["cityName"] if "cityName" in record else None
                comment = record['comment'] if "comment" in record else None
                
                continentName = continentName if continentName else ''
                countryName = countryName if countryName != continentName else '' 
                provinceName = provinceName if provinceName != countryName else ''
                cityName = cityName if cityName else ''
                comment = comment if comment else ''
                # logger.info('record : %r',sd)

                if cityName:
                    currentConfirmedCount = record["city_currentConfirmedCount"] if "city_currentConfirmedCount" in record else None
                    confirmedCount = record["city_confirmedCount"] if "city_confirmedCount" in record else None
                    suspectedCount = record["city_suspectedCount"] if "city_suspectedCount" in record else None
                    curedCount = record["city_curedCount"] if "city_curedCount" in record else None
                    deadCount = record["city_deadCount"] if "city_deadCount" in record else None

                    currentConfirmedCount = currentConfirmedCount if currentConfirmedCount else 0
                    confirmedCount = confirmedCount if confirmedCount else 0
                    suspectedCount = suspectedCount if suspectedCount else 0
                    curedCount = curedCount if curedCount else 0
                    deadCount = deadCount if deadCount else 0                    

                    cityRow.append(sd)
                    cityRow.append(continentName)
                    cityRow.append(countryName)
                    cityRow.append(provinceName)                            
                    cityRow.append(cityName)
                    cityRow.append(currentConfirmedCount)
                    cityRow.append(confirmedCount)
                    cityRow.append(suspectedCount)
                    cityRow.append(curedCount)
                    cityRow.append(deadCount)
                    cityRow.append(comment)
                    # logger.info('cityRow=%r\n',cityRow)    
                    rows.append(cityRow)
                    cityRow=[]
                else:
                    currentConfirmedCount = record["province_currentConfirmedCount"] if "province_currentConfirmedCount" in record else None
                    confirmedCount = record["province_confirmedCount"] if "province_confirmedCount" in record else None    
                    suspectedCount = record["province_suspectedCount"] if "province_suspectedCount" in record else None
                    curedCount = record["province_curedCount"] if "province_curedCount" in record else None
                    deadCount = record["province_deadCount"] if "province_deadCount" in record else None

                    currentConfirmedCount = currentConfirmedCount if currentConfirmedCount else 0
                    confirmedCount = confirmedCount if confirmedCount else 0
                    suspectedCount = suspectedCount if suspectedCount else 0
                    curedCount = curedCount if curedCount else 0
                    deadCount = deadCount if deadCount else 0                      

                    provinceRow.append(sd)
                    provinceRow.append(continentName)
                    provinceRow.append(countryName)
                    provinceRow.append(provinceName)                            
                    provinceRow.append(cityName)
                    provinceRow.append(currentConfirmedCount)
                    provinceRow.append(confirmedCount)
                    provinceRow.append(suspectedCount)
                    provinceRow.append(curedCount)
                    provinceRow.append(deadCount)
                    provinceRow.append(comment)
                    # logger.info('provinceRow=%r\n',provinceRow)
                    rows.append(provinceRow)
                    provinceRow=[]
        logger.info('len(row)=%r',len(rows))
        name = 'NCP'
        columns = ["update","continentName","countryName","provinceName","cityName","currentConfirmedCount","confirmedCount","suspectedCount","curedCount","deadCount","comment"]
        # SQL = f"""insert into {name} ({','.join(columns)}) values ({','.join(['%s'] * len(columns))});"""
        SQL = f"""
            insert into "{name}" ("{'","'.join(columns)}") values ({','.join(['%s'] * len(columns))})
            ON CONFLICT ON CONSTRAINT ncp_unique 
            DO UPDATE SET 
            "currentConfirmedCount" = EXCLUDED."currentConfirmedCount",
            "confirmedCount" = EXCLUDED."confirmedCount",
            "suspectedCount"= EXCLUDED."suspectedCount",
            "curedCount" = EXCLUDED."curedCount",
            "deadCount" = EXCLUDED."deadCount",
            "comment" = EXCLUDED."comment"               
            ;
        """        
        psql.cursor.executemany(SQL,rows)
        psql.conn.commit()
                  
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog = 'crawl NCP',description = '爬取新冠肺炎数据,默认爬取当天最新数据')
    parser.add_argument("-a","--all",action="store_true",help='获得网站全部新冠肺炎数据，本地数据将被清除。')
    parser.add_argument("-c","--cvs",help='从指定csv文件中提取数据')
    parser.add_argument("-j","--json",help='从指定json文件中提取数据')
    args = parser.parse_args()        
    # dbname = 'COVID-19'
    # user='operator'
    # password='5302469'
    # # host='localhost'
    # host='127.0.0.1'
    # port='2012'
    # psql = MyPostgreSQL(dbname=dbname,user=user,password=password,host=host,port=port)    
    # if args.all:
    #     filename = 'DXYArea-TimeSeries.json'
    #     with open(filename,'r',encoding='utf-8',errors='ignore') as f:
    #         records=json.load(f)
    #         DBSave(records)
    #     filename = 'DXYOverall-TimeSeries.json'                   
    #     with open(filename,'r',encoding='utf-8',errors='ignore') as f:
    #         records=json.load(f)
    #         extra = {'continentName':'亚洲','countryName':'中国'}
    #         DBSave(records,**extra)        
    # if args.cvs:
    #     filename = args.cvs
    #     DXY_csv_to_database(filename)
    # if args.json:
    #     filename = args.json
    #     with open(filename, 'r') as f:
    #         data = json.load(f)
            # logger.info('type(data)=%r',type(data))
    p1 = multiprocessing.Process(target=crawl_NCP)
    p2 = multiprocessing.Process(target=crawl_NCP_qq)

    p1.start()
    p2.start()
    # url = 'https://ncov.dxy.cn/ncovh5/view/pneumonia'
    # crawl_NCP_dingxiang(url=url,timeout=timeout)