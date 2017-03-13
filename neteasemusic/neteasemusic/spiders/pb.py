# -*- coding:utf-8 -*-

from scrapy import spider
import requests
from scrapy.selector import Selector                  #导入提取器
from neteasemusic.items import NeteasemusicItem                       #这里是导入了我们的item.py 里我们自己定义的类
from selenium import webdriver  #针对iframe框架内容操作

class nem(spider.Spider):
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS':{
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/user/home?id=50687267',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
            }
    }
    name='haibara'
    start_urls=[
        "http://music.163.com/#/user/home?id=50687269"
    ]
    use_urls="http://music.163.com/#/user/home?id=50687269"     #用于selenium所用解析.所以此爬虫可以不用scrapy来写 (后面id请自己改)
    uni_url="http://music.163.com"             #用于连接歌单前缀
    allowed_domains=["music.163.com"]

    #将iframe内容转换为可解析的html
    # driver = webdriver.PhantomJS()
    # driver.get(start_urls)
    # driver.switch_to.frame("g_iframe")
    # html = driver.page_source


    def frame_to_parse(self,url):
        #动态框架转换为可提取的网页
        driver = webdriver.PhantomJS()
        driver.get(url)
        driver.switch_to.frame("g_iframe")
        html = driver.page_source
        return html


    def parse(self, response):
        sel=Selector(response)
        item=NeteasemusicItem()
        #list_title=Selector(text=self.html).xpath('//*[@class="msk"]/@title').extract()
        html=self.frame_to_parse(self.use_urls)
        list_link=Selector(text=html).xpath('//*[@class="msk"]/@href').extract()
        for each_link in list_link:
            #进入每个歌单的链接地址
            cur_list=self.uni_url+each_link
            in_list=requests.get(cur_list)  #本歌单链接返回请求
            song_link=Selector(in_list).xpath('//ul[@class="f-hide"]/li/a/@href').extract()
            #song_title=Selector(in_list).xpath('//ul[@class="f-hide"]/li/a/text()').extract()
            for each_song_link in song_link:
                #进入每首歌的链接地址
                cur_song=self.uni_url+each_song_link
                in_song=requests.get(cur_song)
                html=self.frame_to_parse(cur_song)
                title=Selector(text=html).xpath('//div[@class="tit"]/em/text()').extract()
                credits=Selector(text=html).xpath('//span[@id="cnt_comment_count"]/text()').extract()
                singer=Selector(text=html).xpath('//span/a[@class="s-fc7"]/text()').extract()
                for it in title:
                    it.encode('utf-8')
                for it in credits:
                    it.encode('utf-8')
                for it in singer :
                    it.encode('utf-8')
                item['title']=title
                item['credits']=credits
                item['singer']=singer
                item['link']=[cur_song]
                yield item
