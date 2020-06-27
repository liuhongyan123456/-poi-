# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 12:51:18 2020

@author: User
"""
import os
import pandas as pd
import requests as re
from  lxml import etree
import json
import math
import shapefile
'''


'''
#获取全部数据的网址
def read_url(address,city):
    url='https://restapi.amap.com/v3/place/text?keywords={}&city={}&offset=20&page=1&key=c2241b021ddebdf69c6848acd22e8eeb&extensions=all'.format(address,city)
    url=re.get(url).text
    data=json.loads(url)
    count=data["count"]
    pages = math.ceil(int(count)/20)  # 算出一共需要的总页数,向上取整
    urls=[]
    for page in range(1, pages + 1):
        ur2='https://restapi.amap.com/v3/place/text?keywords={}&city={}&offset=20&page={}&key=c2241b021ddebdf69c6848acd22e8eeb&extensions=all'.format(address,city,page)
        urls.append(ur2)
    return urls

#爬取14页麦当劳数据
def read_json(address,city):
    urls=read_url(address,city)
    for url in urls:
        url=re.get(url).text
        data=json.loads(url)
        da=[]
        for i in range(len(data['pois'])):
            dt={}
#            dt['id']=data['pois'][i]['id']
#            dt['tag']=data['pois'][i]['tag']
            dt['address']=data['pois'][i]['address']
            dt['location']=data['pois'][i]['location']
#            dt['lat']=data['pois'][i]['location'].split(',')[0]
#            dt['lng']=data['pois'][i]['location'].split(',')[0]
            da.append(dt)
        df=pd.DataFrame(da) #获取每一个网页的数据
#        df=pd.DataFrame(da,columns=["address","lat","lng"]) #获取每一个网页的数据
        df.to_csv('./POI.csv',mode='a',header=False, index=False,encoding='gbk')#mode="a"采用追加的形式存储
        print(url,"存储完成")
        print(".................")
    print("All data is finished!")
        
    
#def read_json(address,city):
#    url='https://restapi.amap.com/v3/place/text?keywords={}&city={}&offset=20&page=1&key=c2241b021ddebdf69c6848acd22e8eeb&extensions=all'.format(address,city)
#    url=re.get(url).text
#    data=json.loads(url)
#    da=[]
#    for i in range(len(data['pois'])):
#        dt={}
#        dt['id']=data['pois'][i]['id']
#        dt['address']=data['pois'][i]['address']
#        dt['location']=data['pois'][i]['location']
#        da.append(dt)
#    print(da)


# 其他坐标的转换方法见：GCJ02(火星坐标系)转GPS84
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]



def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

def polit_to_wgs84(x):
    
    lng=float(x.split(',')[0])#数据需要转换为浮点型
    lat=float(x.split(',')[1])
    
    return gcj02_to_wgs84(lng, lat)

def lines_wgs84(x):
    lst = []
    for i in x: #每一列lines中的列表数据进行for循环
#        print(i)
        lng = float(i.split(',')[0])
        lat = float(i.split(',')[1])
        lst.append(gcj02_to_wgs84(lng,lat))
    return lst

if __name__=='__main__':
    address='麦当劳'
    city='北京'
#    urls=read_url(address,city)
#    read_json(address,city)
    d=pd.read_csv('POI.csv',encoding='gbk', names=["address","location"])
    d["point_to_wgs84"]=d["location"].apply( polit_to_wgs84)

    
    #创建点矢量文件
    w=shapefile.Writer("麦当劳_point.shp")
    w.field("name",'C')#创建字段
    for i in range(len(d['point_to_wgs84'])):
        w.point(d['point_to_wgs84'][i][0],d['point_to_wgs84'][i][1])
        w.record(d["address"][i].encode('gbk'))
    w.close()
#    url='https://restapi.amap.com/v3/place/text?keywords={}&city={}&offset=20&page=1&key=c2241b021ddebdf69c6848acd22e8eeb&extensions=all'.format(address,city)
#    url=re.get(url).text
#    data=json.loads(url)
#    
#    print(data['pois'][0]['location'].split(','))
#    
    


