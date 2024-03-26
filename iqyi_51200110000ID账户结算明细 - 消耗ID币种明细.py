from selemniu import webdriver
import time
import csv
import math

#import numpy as np
import xlrd
import datetime
#from xlutils import copy

from collections import OrderedDict
from pyexcel_xls import get_data
from pyexcel_xls import save_data

import os #创建文件夹
import requests
from bs4 import BeautifulSoup  ##用于读取网页数据
from __config_IQY_finItem_51200110000 import mail,pwd,datebg,dateend,ts,uidlist,adminid


#driver =webdriver.Chrome()
#driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe') #启动chrome 
driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe') #启动chrome 
mytime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
print("第1次启动chrome时间:"+mytime)
driver.get("https://tuiguang.iqiyi.com/")
#print("---控制浏览器大小")
#driver.set_window_size(800,600)
driver.maximize_window()

print("---开始模拟点击")
driver.find_element_by_css_selector("#app > div:nth-child(1) > div > div > div.header-fr > a:nth-child(1)").click()

print("---等待2s")
time.sleep(2)

print("---输入帐号")
driver.find_element_by_css_selector("#app > div:nth-child(1) > div:nth-child(4) > div > div > div:nth-child(3) > div.dialog-input > div.dialog-input-item.dialog-input-number > input[type=text]").send_keys(mail)
print("---输入密码")
driver.find_element_by_css_selector("#app > div:nth-child(1) > div:nth-child(4) > div > div > div:nth-child(3) > div.dialog-input > div.dialog-input-item.dialog-input-password > input[type=password]").send_keys(pwd)
print("---点击登录")
driver.find_element_by_css_selector("#app > div:nth-child(1) > div:nth-child(4) > div > div > div:nth-child(3) > button").click()

time.sleep(2)

mytime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
print("第2次登录网页时间:"+mytime)
#https://tuiguang.iqiyi.com/platform/account/agent
#https://tuiguang.iqiyi.com/platform/homepage/agents
if driver.current_url =="https://tuiguang.iqiyi.com/platform/homepage/agents" :
    print("登陆成功")
else:
    print("登陆不成功")
    quit()

#step1 读取cookie值
cookie_list=driver.get_cookies()
cookies=""
for cookie in cookie_list :
    if cookie['value']=="":
        cookie['value']=str(1)
    cookies=cookies+cookie['name']+"="+cookie['value']+"; "
cookies=cookies[:-2]
#print(cookies)


#cookies="qxga=group-b|828; qxps=SWthzYU3yMP4e8cP3UmaMkgsXUFMpIPq3yTeueDF3gRZkz86WsTquU_x4SX0g8g0OhshummoprXRP8oarnos282BxMSKDPhNT3om87q-cxH-rhDDLMdwGkJ4enhCtW-uZJcxH8ZK1S-bjHDTPPeOgI1w7pBZwQt7z0_XYngDUU0; __dfp=a1d733b2117acf41d7a337af93e69488b1efb59a32414188aa51d4d3e524da5b97@1578388112619@1577092113619; SESSION-ID=6c7bb7b9-c2f3-4088-ab1b-30f8080014ef"
headers = {
    'Host':'tuiguang.iqiyi.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'cookie': cookies,
    #访问的cookie   
}

startTime=time.time()


print("请注意==>消耗数据最大时间范围是31天<==")
print("现在抓取从"+str(datebg)+"到"+str(dateend)+"期间所有消耗数据")

j=1
#创建Excel文档
data = OrderedDict()
mysheet=[]
title=['序号','结算时间','客户ID','现金金额','虚拟金金额','总金额','交易类型','交易类型ID','Puid','Pname','OPId','memo','adminid','爬虫抓取时间']
#chargeinfo=[j,date,uid,cash,virtual,balance,trans_type,trans_typeID,Puid,Pname,OPId,memo,adminid,dateedit]

mysheet.append(title)
myxls="iqy_uidItems_statement_detail_"+str(adminid)+"_"+str(datebg)+"&"+str(dateend)+"_"+str(time.strftime("%Y%m%d%H%M%S",time.localtime()))
  
def request_totalpage (var_page,uid):
    #针对没有总页码的request查询
    #现金账号==>0
    page_size=100
    url="https://tuiguang.iqiyi.com/finance/ajax/advertiser/financeRecord/"+str(uid)
    params = {
        "start": page_size*(var_page-1),
        "count": page_size,
        "startDay":str(datebg),
        "endDay":str(dateend),
        "detailTypes": [],
    }
 
    try:
        #response = requests.get(url,headers=headers,timeout=ts)
        response = requests.put(url, json=params,headers=headers,timeout=ts)
        if response.status_code==200:
            global j
            global mysheet
            print("xmlhttp响应正常,开始抓取对应的消耗结算数据")
            response.enconding = "utf-8"
            response_json=response.json()

            total_rows=response_json["totalRows"]  #返回结果总行数
            total_page=math.ceil(total_rows/page_size)
            data_list=response_json["recordDetails"]
            
            print("现在抓取第"+str(var_page)+"页数据，共"+str(total_page)+"页")

            for datalist in data_list:
                date=datalist["operationDate"]  ##结算时间
                balance=datalist["balanceVO"]["balance"]  #合计
                cash=datalist["balanceVO"]["cash"]  #现金
                virtual=datalist["balanceVO"]["virtual"]  #虚拟金

                trans_type=datalist["transactionTypeName"]  #交易类型
                
                trans_typeID=datalist["transactionType"]  #交易类型id
                
                

                Puid=str(datalist["partnerId"])
                Pname=datalist["partnerName"]
                OPId=str(datalist["transactionRecordId"])
                memo=datalist["reason"]
       
                
  
                dateedit=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                chargeinfo=[j,date,str(uid),cash,virtual,balance,trans_type,trans_typeID,Puid,Pname,OPId,memo,adminid,dateedit]
                #print(chargeinfo)
                #print(next_page_check,var_page)
                mysheet.append(chargeinfo)
                j=j+1

            var_page=var_page+1

    except  BaseException as e:
        print("出现异常"+str(e))
        quit()

    return total_page,var_page


def request_totalpage_while (uid): 
    mypage=1 
    total_page=1
    while mypage <=total_page:
        ##一直循环到当前页面大于总页面
        total_page,mypage = request_totalpage (mypage,uid)
        
for myid in uidlist :
    print("--"+str(myid)+"--")
    request_totalpage_while (myid)


data.update({"sheet1":mysheet}) #数据更新到sheet1
save_data(myxls+".xls",data)
endtime=time.time()
print('合计用时%.2f' % (endtime-startTime))


