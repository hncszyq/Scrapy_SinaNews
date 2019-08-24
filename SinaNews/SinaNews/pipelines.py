# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb

class SinanewsPipeline(object):
    db = MySQLdb.connect("localhost","root","123456789-zyq","news",charset="utf8mb4")
    cursor = db.cursor()
    def process_item(self, item, spider):
        sql = "insert into `Sina` \
               (`title`,`date`,`editor`,`url`,`content`) \
               values (%s,%s,%s,%s,%s)" % \
              ("'"+item['title']+"'","'"+item['date']+"'","'"+item['editor']+"'","'"+item['url']+"'","'"+item['content']+"'")
        self.cursor.execute(sql)
        self.db.commit()
        return item
    def open_spider(self,spider):     
        self.cursor.execute("drop table if exists Sina") 
        sql = """create table `Sina` (
                 `count` int unsigned auto_increment,
                 `title` varchar(100),
                 `date` varchar(40),
                 `editor` varchar(40),
                 `url` varchar(100),
                 `content` mediumtext,
                 primary key (`count`)
                 )engine=InnoDB default charset=utf8mb4;"""
        self.cursor.execute(sql)
        self.db.commit()
    def close_spider(self,spider):
        self.db.close()
