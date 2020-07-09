# -*- coding: utf-8 -*-

import os

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class S1Pipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv("MONGO_URL"))
        self.db = self.client.get_database("s1")

    def process_item(self, item, spider):
        if item["type"] == "thread":
            self.db.threads.update_one({"tid": item["tid"]}, {"$set": item}, upsert=True)
        elif "index" in item:
            self.db.replies.update_one({"tid": item["tid"], "index": item["index"]}, {"$set": item}, upsert=True)
        return item
