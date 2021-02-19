# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:49:33 2020

@author: :Dain
"""

# 공공데이터 포털에서 지자체별 월별 코로나 확진자수 데이터 수집 

import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import numpy as np
import pandas as pd

API_URL = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
API_KEY =unquote('input your API key')

params = dict()
params['serviceKey'] = API_KEY
params['pageNo']=1
params['numOfRows']=200   
params['startCreateDt']='20200101'  # start date
params['endCreateDt']='20201231' # end date
r = requests.get(API_URL, params=params)
print(r.text)
print(r.url)
        
soup=BeautifulSoup(r.content,'html.parser')
data=soup.find_all('item')

covid_date=[]
city=[]
patients=[]

for item1 in range(len(data)):
    print(item1)
    item=data[item1]
    date= item.find('stdday') 
    stationname=item.find('gubun')
    cnt=item.find('defcnt')
    cnt=item.find('incdec')
    
    #print(date.get_text(),stationname.get_text(),cnt.get_text())
                    
    
    covid_date=covid_date+[date.get_text()]
    city=city+[stationname.get_text()]
    if cnt!=None:
        patients=patients+[cnt.get_text()]
    else: patients=patients+['0']


#to dataframe
covid=pd.DataFrame({'covid_date':covid_date,'city':city,'patients':patients})
covid1=covid

# date
month=pd.to_numeric(covid1.covid_date.str.split(' ',expand=True)[1].str.replace('월',""))
day=pd.to_numeric(covid1.covid_date.str.split(' ',expand=True)[2].str.replace('일',""))
formater = lambda x:" %.02d" %(x)
month1=month.map(formater)
day1=day.map(formater)

#insert date to covid dataframe
covid1['date']='2020'+month1+day1
covid1['year']=2020
covid1['month']=month1
covid1['day']=day1

#wide-area unit of local government
city=pd.DataFrame({'서울':1, '부산':2, '대구':3, '인천':4, '광주':5,'대전':6,'울산':7,'세종':8,'경기':9,'강원':10,'충북':11,'충남':12,'전북':13,'전남':14,'경북':15,'경남':16,'제주':17,'합계':18},index=[0]).T.reset_index()
city.columns=['city','city_no']

#merge city and covid
covid2=pd.merge(covid1,city,on=['city'],how='outer')

#order
covid3=covid2.sort_values(['date','city_no'],ascending=[True,True])

#drop duplicates
covid4=covid3.drop_duplicates(['month','day','city'],keep='first')
#covid3[covid3.duplicated()==True] #중복된 항목이 뭐지

#pivot table of yearly covid data
covid_pv=covid4.pivot(index=['year','month','day'],columns='city',values='patients').reset_index()
covid_data=pd.DataFrame(covid_pv)
covid_data=covid_data[['year','month','day',"서울",'부산','대구','인천','광주','대전','울산','세종','경기','강원','충북','충남','전북','전남','경북','경남','제주','합계']].apply(pd.to_numeric)

#pivot table of monthly covid data
monthly_covid_data=covid_data.groupby(['year','month'])[["서울",'부산','대구','인천','광주','대전','울산','세종','경기','강원','충북','충남','전북','전남','경북','경남','제주','합계']].agg(sum)

