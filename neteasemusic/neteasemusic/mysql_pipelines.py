# -*- coding:utf-8 -*-

from scrapy.conf import settings
import MySQLdb
from hashlib import md5

_DEBUG=True

class MySQLPipeline(object):
    #Connect to the MySQL database
    def __init__(self):
        self.conn =MySQLdb.connect(
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            db=settings['MYSQL_DBNAME'],
            host=settings['MONGODB_HOST'],
            charset='utf8',
            use_unicode = True
        )
        self.cursor=self.conn.cursor()
        self.cursor.execute("truncate table neteaseinfo;") #清空表的信息
        self.conn.commit()

    def process_item(self, item, spider):
        try:
            self.insert_all(item)
            self.conn.commit()

        except MySQLdb.Error as e:
            print (("Error %d: %s") % (e.args[0],e.args[1]))
        return item

    #将信息插入到数据库中
    def insert_all(self,item):
        linkmd5id = self._get_linkmd5id(item)
        args=(str(linkmd5id),str(item["title"]),str(item["singer"]),str(item["credits"]))

        allSqlText="insert into neteaseinfo(linkmd5id, title, singer, credits)"\
                   "values ('%s','%s','%s','%s')" % args

        self.cursor.execute(allSqlText)
        self.conn.commit()

    #获取url的md5编码
    def _get_linkmd5id(self, item):
        #url进行md5处理，为避免重复采集设计
        return md5(str(item['link'])).hexdigest()

