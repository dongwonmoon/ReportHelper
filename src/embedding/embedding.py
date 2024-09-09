import pymongo
from pymongo import MongoClient

import chromadb

from transformers import AutoTokenizer, AutoModel
import torch

def tokenize(model, tokenizer, text):
    '''
    return 1: model_output -> embedding(0)
    return 2: attention_mask -> padding 구분
    '''
    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
    return model_output, encoded_input['attention_mask']

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] # token
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def insert_chroma_db(data, embeddings, idx):
    content = data['content']
    content = ' '.join(content.split())
    content = ''.join(char for char in content if char.isalnum() or char.isspace())
    
    meta_data = {
        'title': data['title'],
        'content': content,
        'summarized': data['summarized']
    }
    
    paper_embeddings.add(
        metadatas=[meta_data],
        embeddings=embeddings.numpy().tolist(),
        ids=[str(idx)]
    )

# embedding 모델 준비
tokenizer = AutoTokenizer.from_pretrained('jhgan/ko-sroberta-multitask')
model = AutoModel.from_pretrained('jhgan/ko-sroberta-multitask')

# MongoClient
conn = MongoClient('mongodb://localhost:27017/')

db_name = 'report_helper_papers'
db = conn.get_database(db_name)
collection = db['papers']

datas = collection.find({}, {"title": 1, "pages": 1, "content": 1, "summarized": 1})

# Chromadb
client = chromadb.PersistentClient()

collection_name = "paper_embeddings"
try:
    paper_embeddings = client.get_collection(name=collection_name)
except:
    paper_embeddings = client.create_collection(name=collection_name)

for idx, data in enumerate(datas):
    model_output, attention_mask = tokenize(model, tokenizer, data['summarized'])
    embeddings = mean_pooling(model_output, attention_mask)
    
    insert_chroma_db(data, embeddings, idx)