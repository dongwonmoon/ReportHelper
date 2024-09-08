import pymongo
import json
from pymongo import MongoClient
import os
from collections import OrderedDict

# cmd에서 mongod 실행 후 파이썬 실행

conn = MongoClient('mongodb://localhost:27017/')

db_name = 'report_helper_papers'
db = conn.get_database(db_name)
collection = db['papers']

json_dir = 'ReportHelper/data/json'

for json_name in os.listdir(json_dir):
    insert_data = dict()
    if json_name.endswith('.json'):
        json_path = os.path.join(json_dir, json_name)
        
        with open(json_path, 'r', encoding='utf-8') as file:
            file_data = json.load(file)
            
        title = os.path.splitext(json_name)[0]
        
        pages = list()
        for page_n in file_data.keys():
            page = file_data.get(page_n, {})
            pages.append(page)
        
        content = "\n".join(pages)
        
        insert_data['title'] = title
        insert_data['pages'] = file_data
        insert_data['content'] = content
        
        collection.insert_one(insert_data)
        
        print(f'{title} 논문이 저장되었습니다.')