from pymongo import MongoClient
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import torch

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# 1. MongoDB 연결 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['report_helper_papers']
collection = db['papers']

# 2. Pegasus 모델 및 토크나이저 로드
tokenizer = PreTrainedTokenizerFast.from_pretrained('digit82/kobart-summarization')
model = BartForConditionalGeneration.from_pretrained('digit82/kobart-summarization')

# 3. MongoDB에서 title과 content 가져오기
# 모든 논문의 title과 content 필드를 가져옴
papers = collection.find({}, {"title": 1, "pages": 1, "content": 1})

# 4. 요약 작업 함수
def summarize(text):
    text = ' '.join(text.split())
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    text = f"다음 논문의 핵심을 요약해 주세요: \n\n {text}"
    
    max_length = 512
    inputs = tokenizer.encode(text, return_tensors="pt", truncation=True, max_length=max_length)
    
    # 요약 생성
    summary_ids = model.generate(
        inputs,
        num_beams=4,
        max_length=150,
        length_penalty=2.0,
        early_stopping=True,
        eos_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=2 
    )
    
    # 토큰을 텍스트로 변환하여 요약문 반환
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary

def insert_paper(title, file_data, content):
    summary = summarize(content)
    
    # MongoDB에 삽입할 데이터 구성
    insert_data = {
        'title': title,
        'pages': file_data,
        'content': content,
        'summarized': summary  # 요약된 내용을 추가
    }
    
    # 데이터 업데이트 또는 삽입
    collection.update_one(
        {'title': title},  # 조건: title이 같은 문서 찾기
        {'$set': insert_data},  # 업데이트할 내용
        upsert=True  # 조건에 맞는 문서가 없으면 새로 추가
    )

# 5. 각 논문의 title과 content를 출력하고 content를 요약
for paper in papers:
    title = paper.get("title")
    pages = paper.get("pages")
    content = paper.get("content")
        
    insert_paper(title, pages, content)