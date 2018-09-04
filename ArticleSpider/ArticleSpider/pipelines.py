# -*- coding: utf-8 -*-

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter     #自带的文件保存格式
from twisted.enterprise import adbapi

import codecs
import json

import MySQLdb
from MySQLdb import cursors

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item



"""自定义保存json数据的中间件"""
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json","w",encoding="utf-8")

    #将item以json格式写入文件
    def process_item(self, item, spider):
        lines = json.dumps(dict(item),ensure_ascii=False) + "\n"
        self.file.write(lines)

        return item
    #在spider关闭时，关闭spider
    def spider_closed(self,spider):
        self.file.close()



"""继承scrapy 提供的 json exporter 导出json文件"""
class JsonExporterPipeline(object):

    def __init__(self):
        self.file = open('articleExport.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding="utf-8",ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item





"""使用自定义的中间件，继承，实现定制装载图片路径到item"""
class ArticleImagePipeline(ImagesPipeline):
    #重载
    def item_completed(self, results, item, info):

        if "front_image_url" in item:
            for ok,value in results:
                image_file_path = value["path"]
                item["front_image_path"] = image_file_path #'full/14452eea6b79bce0219227f298ad827f2ba7112d.jpg'

            return item


"""使用自定义的插入数据库方式，同步操作"""
class MysqlPipeline(object):

    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1','root','110811','article_spider',charset="utf8",use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title,url,create_date,fav_nums)
            values (%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item["title"],item["url"],item["create_date"],item["fav_nums"]))
        self.conn.commit()


"""Mysql连接池，异步"""
class MysqlTwistedPipeline(object):

    def __init__(self,dbpool):
        self.dbpool = dbpool

    #加载setting中的变量
    @classmethod
    def from_settings(cls,settings):
        dbparms = dict(
        host = settings["MYSQL_HOST"],
        db = settings["MYSQL_DBNAME"],
        user = settings["MYSQL_USER"],
        passwd = settings["MYSQL_PASSWORD"],
        charset = 'utf8',
        cursorclass = MySQLdb.cursors.DictCursor,
        use_unicode = True,
        )

        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)

        return cls(dbpool)


    def process_item(self, item, spider):
        #使用Twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error) #处理异常
        return item

    '''处理异步插入的异常'''
    def handle_error(self, failure):
        print(failure)

    def do_insert(self,cursor,item):
        #执行具体的插入
        insert_sql = """
                       INSERT INTO jobbole_article(title,create_date,url,url_object_id,
                       front_image_url,front_image_path,comment_nums,fav_nums,praise_nums,
                       tags,content)
                       VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)
                       """

        front_image_url = ""
        if item["front_image_url"] :
            front_image_url = item["front_image_url"][0]

        cursor.execute(insert_sql, ( item['title'], item["create_date"],item['url'], item['url_object_id'],
                                     front_image_url,item["front_image_path"],item["comment_nums"],
                                     item["fav_nums"],item["praise_nums"],item["tags"],item["content"]
                                     ))




