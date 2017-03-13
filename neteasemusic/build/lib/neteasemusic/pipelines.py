# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


#利用新的pipeline是保存数据的方法

import json
import codecs
from twisted.enterprise import adbapi
from hashlib import md5
import MySQLdb
import MySQLdb.cursors


class JsonWithEncodingCnblogsPipeline(object):
    def __init__(self):
        self.file = codecs.open('netease.json', 'w', encoding='utf-8')
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
    def spider_closed(self, spider):
        self.file.close()


class WebcrawlerScrapyPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)

        return cls(dbpool)

    #pipeline默认调用
    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d
    #将每行更新或写入数据库中
    def _do_upinsert(self, conn, item, spider):
        linkmd5id = self._get_linkmd5id(item)
        conn.execute("""
                select 1 from neteaseinfo where linkmd5id = %s
        """, (linkmd5id, ))
        ret = conn.fetchone()

        if ret:
            print "have existed"
            pass
            #conn.execute("""
            #    update neteaseinfo set title = %s, singer = %s ,credits=%s where linkmd5id = %s
            #""", (str(item['title']).encode('utf-8'), str(item['singer']), str(item['credits']), str(linkmd5id)))

        else:
            print "success for insert "
            conn.execute("""
                insert into neteaseinfo(linkmd5id, title, singer, credits)
                values(%s, %s, %s, %s )
            """, (str(linkmd5id), str(item['title']), str(item['singer']), str(item['credits'])))

    #获取url的md5编码
    def _get_linkmd5id(self, item):
        #url进行md5处理，为避免重复采集设计
        return md5(str(item['link'])).hexdigest()
    #异常处理
    def _handle_error(self, failure, item, spider):
        print failure


